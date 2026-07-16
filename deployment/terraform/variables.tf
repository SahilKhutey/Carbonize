variable "aws_region" {
  description = "Target AWS deployment region"
  type        = string
  default     = "ap-south-1"  # Mumbai
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "db_username" {
  description = "Admin database username"
  type        = string
  default     = "postgres"
}

variable "s3_bucket_name" {
  description = "Globally unique bucket name for PDF reports and ML assets"
  type        = string
  default     = "cbms-validation-reports-bucket"
}
