# Carbonize AWS Production Deployment
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "environment" {
  type    = string
  default = "production"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "tier" {
  type    = string
  default = "medium"
}

variable "domain_name" {
  type    = string
  default = "carbonize.io"
}

locals {
  name_prefix = "carbonize-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = "Carbonize"
    ManagedBy   = "Terraform"
  }
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = merge(local.tags, { Name = "${local.name_prefix}-vpc" })
}

output "vpc_id" {
  value = aws_vpc.main.id
}
