### Terraform vars to create a VPC with public and private subnets in AWS ###
aws_region          = "eu-north-1"
vpc_cidr            = "10.0.0.0/16"
vpc_private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
vpc_public_subnets  = ["10.0.3.0/24", "10.0.4.0/24"]
vpc_name            = "365scores-vpc"


project_name        = "365"

### Terraform vars to create the ALB ###
certificate_arn     = "arn:aws:acm:eu-north-1:194722398257:certificate/484cb8cf-5660-48e5-af42-d6369bd3af24"

### Terraform vars to create the Route53 records ###
environment         = "dev"
domain_name         = "shaharshitrit.com"  # Placeholder domain
subdomain           = "www"

### Terraform vars to create the SG ###
http_port           = 80
https_port          = 443
protocol            = "tcp"
sg_cidr_blocks      =  ["0.0.0.0/0"]
egress_from_port    = 0
egress_to_port      = 0

