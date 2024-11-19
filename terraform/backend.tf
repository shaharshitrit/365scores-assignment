terraform {
  backend "s3" {
    bucket         = "365scores-assignment-bucket"
    key            = "aws-eks-cluster/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-lock-table"
    encrypt        = true
  }
}
