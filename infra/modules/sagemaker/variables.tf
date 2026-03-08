variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "sagemaker_execution_role_arn" {
  description = "Execution role ARN for SageMaker"
  type        = string
}
