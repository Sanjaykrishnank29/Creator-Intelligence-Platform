# Note: Creating a SageMaker model requires a model artifact in S3.
# For the hackathon MVP infra, we are creating the endpoint configuration
# and endpoint, but the actual model generation will happen via Python script
# (SageMaker Training Job). 

# We create the Endpoint Config for Serverless Inference.
# We will leave the model name as a placeholder or expect it to be passed
# once the training pipeline runs.

resource "aws_sagemaker_endpoint_configuration" "serverless_ep_config" {
  name = "${var.project_name}-${var.environment}-serverless-config"

  production_variants {
    variant_name            = "AllTraffic"
    # Placeholder model name until dynamic mapping or initial deploy
    model_name              = "${var.project_name}-${var.environment}-xgboost-model" 
    
    serverless_config {
      max_concurrency   = 10
      memory_size_in_mb = 2048
    }
  }

  tags = {
    Environment = var.environment
    Name        = "ServerlessEndpointConfig"
  }
}

# Real deployment requires the model to exist first, so we use Terraform lifecycle
# to ignore the endpoint creation error or assume it is deployed via SDK later.
# For a pure MVP IaC setup, defining the config is often sufficient if the Python Script
# deploys the actual endpoint. We'll define it here so it's in state.

resource "aws_sagemaker_endpoint" "serverless_endpoint" {
  name                 = "${var.project_name}-${var.environment}-serverless-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.serverless_ep_config.name

  tags = {
    Environment = var.environment
    Name        = "ServerlessEndpoint"
  }
  
  # Ignore config changes explicitly pushed via SDK
  lifecycle {
    ignore_changes = [endpoint_config_name]
  }
}
