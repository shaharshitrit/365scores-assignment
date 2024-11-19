variable "aws_region" {
  description = "AWS region to deploy the EKS cluster"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC cidr ip"
  type        = string
}

variable "vpc_private_subnets" {
  description = "VPC private subnet ips"
  type        = any
}

variable "vpc_public_subnets" {
  description = "VPC public subnet ips"
  type        = any
}

variable "vpc_name" {
  description = "VPC name"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "certificate_arn" {
  description = "The ARN of the imported ACM certificate"
  type        = string
}

variable "environment" {
    description = "The environment name"
    type        = string
}

variable "domain_name" {
  description = "The domain name for the Route53 hosted zone"
  type        = string
}

variable "subdomain" {
  description = "The subdomain to create a CNAME record for"
  type        = string
}

variable "http_port" {
  description = "The port to use for the HTTP listener"
  type        = number
}

variable "https_port" {
  description = "The port to use for the HTTP listener"
  type        = number
}

variable "protocol" {
    description = "The protocol to use for the listener"
    type        = string
}

variable "sg_cidr_blocks" {
    description = "CIDR blocks to allow in the security group"
    type        = any
}

variable "egress_from_port" {
    description = "The start port for the egress rule"
    type        = number
}

variable "egress_to_port" {
    description = "The start port for the egress rule"
    type        = number
}
