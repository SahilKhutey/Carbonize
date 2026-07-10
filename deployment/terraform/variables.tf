variable "aws_region" {
  description = "Target AWS deployment region"
  type        = string
  default     = "ap-south-1"  # Mumbai
}

variable "db_username" {
  description = "Admin database username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Admin database password"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "Globally unique bucket name for PDF reports and ML assets"
  type        = string
  default     = "cbms-validation-reports-bucket"
}
