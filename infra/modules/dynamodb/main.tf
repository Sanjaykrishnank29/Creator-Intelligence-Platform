resource "aws_dynamodb_table" "creator_profiles" {
  name           = "${var.project_name}-${var.environment}-CreatorProfiles"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "creator_id"

  attribute {
    name = "creator_id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Name        = "CreatorProfiles"
  }
}

resource "aws_dynamodb_table" "creator_content" {
  name           = "${var.project_name}-${var.environment}-CreatorContent"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "creator_id"
  range_key      = "content_id"

  attribute {
    name = "creator_id"
    type = "S"
  }
  attribute {
    name = "content_id"
    type = "S"
  }
  attribute {
    name = "topic"
    type = "S"
  }
  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name               = "TopicIndex"
    hash_key           = "topic"
    range_key          = "timestamp"
    projection_type    = "ALL"
  }

  tags = {
    Environment = var.environment
    Name        = "CreatorContent"
  }
}

resource "aws_dynamodb_table" "predictions" {
  name           = "${var.project_name}-${var.environment}-Predictions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "creator_id"
  range_key      = "prediction_id"

  attribute {
    name = "creator_id"
    type = "S"
  }
  attribute {
    name = "prediction_id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Name        = "Predictions"
  }
}

resource "aws_dynamodb_table" "trend_signals" {
  name           = "${var.project_name}-${var.environment}-TrendSignals"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "topic"

  attribute {
    name = "topic"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Name        = "TrendSignals"
  }
}

resource "aws_dynamodb_table" "llm_cache" {
  name           = "${var.project_name}-${var.environment}-LLMCache"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "input_hash"

  attribute {
    name = "input_hash"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Environment = var.environment
    Name        = "LLMCache"
  }
}
