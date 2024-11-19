module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.16.0"

  name                          = var.name
  cidr                          = var.cidr
  azs                           = var.azs
  private_subnets               = var.private_subnets
  public_subnets                = var.public_subnets
  enable_nat_gateway            = var.enable_nat_gateway
  single_nat_gateway            = var.single_nat_gateway
  enable_dns_hostnames          = var.enable_dns_hostnames
  manage_default_security_group = true

  tags = {
    "Name" = var.name
  }
}
