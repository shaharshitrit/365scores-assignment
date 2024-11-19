# modules/alb/outputs.tf

output "alb_dns_name" {
  description = "The DNS name of the ALB"
  value       = module.alb.dns_name
}

output "alb_zone_id" {
  description = "The zone ID of the ALB"
  value       = module.alb.zone_id
}

output "alb_arn" {
  description = "The ARN of the ALB"
  value       = module.alb.arn
}

