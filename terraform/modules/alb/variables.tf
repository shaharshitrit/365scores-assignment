# modules/alb/variables.tf

variable "name" {
  description = "The name of the ALB"
  type        = string
}

variable "vpc_id" {
  description = "The VPC ID where the ALB will be deployed"
  type        = string
}

variable "subnets" {
  description = "A list of subnets to associate with the ALB"
  type        = list(string)
}

variable "security_groups" {
  description = "A list of security group IDs to assign to the ALB"
  type        = list(string)
}

variable "certificate_arn" {
  description = "The ARN of the ACM certificate"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "target_group_name" {
  description = "The name of the target group"
  type        = string
  default     = null
}
