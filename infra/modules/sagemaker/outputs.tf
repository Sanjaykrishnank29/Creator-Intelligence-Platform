output "sagemaker_endpoint_name" {
  value = aws_sagemaker_endpoint.serverless_endpoint.name
}

output "sagemaker_endpoint_config_name" {
  value = aws_sagemaker_endpoint_configuration.serverless_ep_config.name
}
