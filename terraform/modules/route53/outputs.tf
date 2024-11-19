output "zone_id" {
  description = "The ID of the Route53 hosted zone"
  value       = aws_route53_zone.this.zone_id
}

output "cname_record_fqdn" {
  description = "The fully qualified domain name of the CNAME record"
  value       = aws_route53_record.cname.fqdn
}
