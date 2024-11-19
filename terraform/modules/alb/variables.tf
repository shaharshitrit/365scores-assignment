variable "alb_name" {
  description = "Name of the Application Load Balancer"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ALB will be deployed"
  type        = string
}

variable "subnets" {
  description = "List of subnets for the ALB"
  type        = list(string)
}

variable "security_groups" {
  description = "List of security groups for the ALB"
  type        = list(string)
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS listener"
  type        = string
}
