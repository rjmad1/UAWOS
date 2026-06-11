variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = "string"
  default     = "us-east-1"
}

variable "environment" {
  description = "Target deployment environment (dev, staging, prod)"
  type        = "string"
  default     = "staging"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = "string"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = "list(string)"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = "list(string)"
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "db_name" {
  description = "Database name for Postgres RDS"
  type        = "string"
  default     = "marquez"
}

variable "db_user" {
  description = "Database admin user"
  type        = "string"
  default     = "marquez"
}

variable "db_password" {
  description = "Database admin password"
  type        = "string"
  sensitive   = true
  default     = "marquez_secure_pass_2026"
}

variable "container_image_tag" {
  description = "Docker image tag to deploy for UAWOS BFF"
  type        = "string"
  default     = "latest"
}
