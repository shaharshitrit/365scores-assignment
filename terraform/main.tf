module "vpc" {
  source               = "./modules/vpc"
  name                 = var.vpc_name
  cidr                 = var.vpc_cidr
  azs                  = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets      = var.vpc_private_subnets
  public_subnets       = var.vpc_public_subnets
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

}

module "alb_security_group" {
  source = "./modules/security_group"

  name        = "${var.project_name}-alb-sg"
  description = "Security group for the ALB"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = [
    {
      description      = "Allow HTTP from anywhere"
      from_port        = var.http_port
      to_port          = var.http_port
      protocol         = var.protocol
      cidr_blocks      = var.sg_cidr_blocks
      ipv6_cidr_blocks = []
      security_groups  = []
      self             = false
    },
    {
      description      = "Allow HTTPS from anywhere"
      from_port        = var.https_port
      to_port          = var.https_port
      protocol         = var.protocol
      cidr_blocks      = var.sg_cidr_blocks
      ipv6_cidr_blocks = []
      security_groups  = []
      self             = false
    }
  ]

  egress_rules = [
    {
      description      = "Allow all outbound traffic"
      from_port        = var.egress_from_port
      to_port          = var.egress_to_port
      protocol         = "-1"
      cidr_blocks      = var.sg_cidr_blocks
      ipv6_cidr_blocks = []
      security_groups  = []
      self             = false
    }
  ]

  tags = {
    "Name"        = "${var.project_name}-alb-sg"
    "Environment" = var.environment
    "Project"     = var.project_name
  }
}

module "alb" {
  source = "./modules/alb"

  alb_name         = "${var.project_name}-alb"
  vpc_id           = module.vpc.vpc_id
  subnets          = module.vpc.public_subnets
  security_groups  = [module.alb_security_group.security_group_id]
  certificate_arn  = var.certificate_arn
}

# Route53 Module
module "route53" {
  source = "./modules/route53"

  domain_name  = var.domain_name
  subdomain    = var.subdomain
  alb_dns_name = module.alb.lb_dns_name

  environment  = var.environment
  project_name = var.project_name
}

