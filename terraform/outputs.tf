output "vpc_id" {
  value = module.vpc.vpc_id
}

output "security_group_id" {
  description = "The ID of the ALB security group"
  value       = module.alb_security_group.security_group_id
}

output "route53_zone_id" {
  description = "The ID of the Route53 hosted zone"
  value       = module.route53.zone_id
}
