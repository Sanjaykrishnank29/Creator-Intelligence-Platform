output "secrets_manager_api_keys_arn" {
  value = aws_secretsmanager_secret.api_keys.arn
}

output "lambda_exec_role_arn" {
  value = aws_iam_role.lambda_exec.arn
}

output "sagemaker_exec_role_arn" {
  value = aws_iam_role.sagemaker_exec.arn
}
