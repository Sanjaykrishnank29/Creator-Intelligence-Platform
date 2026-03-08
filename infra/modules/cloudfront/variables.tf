variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "static_website_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket for the static website"
  type        = string
}

variable "api_endpoint" {
  description = "API Gateway endpoint"
  type        = string
}
