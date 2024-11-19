# modules/alb/main.tf

module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "9.12.0"

  name               = var.name
  load_balancer_type = "application"

  vpc_id  = var.vpc_id
  subnets = var.subnets

  security_groups = var.security_groups

  # Define the target groups
  target_groups = [
    {
      name        = "${var.name}-tg"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        path                = "/"
        interval            = 30
        timeout             = 5
        healthy_threshold   = 2
        unhealthy_threshold = 2
        matcher             = "200-399"
      }
    }
  ]

  # Define the listeners
  listeners = [
    {
      port     = 80
      protocol = "HTTP"

      default_action = [  # Changed to a list
        {
          type               = "forward"
          target_group_index = 0
        }
      ]
    },
    {
      port            = 443
      protocol        = "HTTPS"
      ssl_policy      = "ELBSecurityPolicy-2016-08"
      certificate_arn = var.certificate_arn

      default_action = [  # Changed to a list
        {
          type               = "forward"
          target_group_index = 0
        }
      ]
    }
  ]

  tags = {
    "Environment" = var.environment
    "Project"     = var.project_name
  }
}
