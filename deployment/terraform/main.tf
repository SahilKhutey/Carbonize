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

# --- NETWORKING (VPC & SUBNETS) ---
resource "aws_vpc" "cbms_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cbms-vpc"
  }
}

resource "aws_subnet" "cbms_public_subnet_a" {
  vpc_id            = aws_vpc.cbms_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "cbms-public-a"
  }
}

resource "aws_subnet" "cbms_public_subnet_b" {
  vpc_id            = aws_vpc.cbms_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "cbms-public-b"
  }
}

# --- SECURITY GROUPS ---
resource "aws_security_group" "db_sg" {
  name        = "cbms-db-sg"
  description = "Allow inbound PostgreSQL traffic"
  vpc_id      = aws_vpc.cbms_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- DATABASE (RDS POSTGRESQL) ---
resource "aws_db_subnet_group" "db_subnets" {
  name       = "cbms-db-subnet-group"
  subnet_ids = [aws_subnet.cbms_public_subnet_a.id, aws_subnet.cbms_public_subnet_b.id]
}

resource "aws_db_instance" "cbms_db" {
  identifier             = "cbms-postgres"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "17.1"
  instance_class         = "db.t4g.micro"
  db_name                = "biomimetic_db"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot    = true
}

# --- STORAGE (S3 BUCKET) ---
resource "aws_s3_bucket" "cbms_reports" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_public_access_block" "cbms_reports_access" {
  bucket = aws_s3_bucket.cbms_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- EKS CLUSTER FOR SERVICES ---
resource "aws_iam_role" "eks_role" {
  name = "cbms-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_role.name
}

resource "aws_eks_cluster" "cbms_cluster" {
  name     = "cbms-eks-cluster"
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids = [aws_subnet.cbms_public_subnet_a.id, aws_subnet.cbms_public_subnet_b.id]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_policy
  ]
}
