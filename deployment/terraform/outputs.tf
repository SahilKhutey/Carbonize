output "vpc_id" {
  description = "VPC ID of the CBMS network"
  value       = aws_vpc.cbms_vpc.id
}

output "db_endpoint" {
  description = "RDS database endpoint for client connections"
  value       = aws_db_instance.cbms_db.endpoint
}

output "s3_bucket" {
  description = "S3 bucket name for reports storage"
  value       = aws_s3_bucket.cbms_reports.id
}

output "eks_endpoint" {
  description = "EKS API server endpoint"
  value       = aws_eks_cluster.cbms_cluster.endpoint
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  value       = aws_secretsmanager_secret.db_secret.arn
}
