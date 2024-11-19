resource "aws_route53_zone" "this" {
  name = var.domain_name

  tags = {
    "Environment" = var.environment
    "Project"     = var.project_name
  }
}

resource "aws_route53_record" "cname" {
  zone_id = aws_route53_zone.this.zone_id
  name    = var.subdomain  # e.g., "www"
  type    = "CNAME"
  ttl     = 300
  records = [var.alb_dns_name]
}
