terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
    }
  }
}

module "dynamodb" {
  source = "./modules/dynamodb"
  project_name = var.project_name
  environment  = var.environment
}

module "s3" {
  source = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
}

module "apigateway" {
  source = "./modules/apigateway"
  project_name = var.project_name
  environment  = var.environment
}

module "cloudfront" {
  source = "./modules/cloudfront"
  project_name = var.project_name
  environment  = var.environment
  
  static_website_bucket_regional_domain_name = module.s3.static_website_bucket_regional_domain_name
  api_endpoint                               = module.apigateway.api_endpoint
}

module "iam" {
  source = "./modules/iam"
  project_name = var.project_name
  environment  = var.environment
}

module "sagemaker" {
  source = "./modules/sagemaker"
  project_name = var.project_name
  environment  = var.environment
  
  sagemaker_execution_role_arn = module.iam.sagemaker_exec_role_arn
}
