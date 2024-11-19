variable "domain_name" {
  description = "The domain name for the Route53 hosted zone"
  type        = string
}

variable "subdomain" {
  description = "The subdomain to create a CNAME record for"
  type        = string
}

variable "alb_dns_name" {
  description = "The DNS name of the ALB to point the CNAME record to"
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
