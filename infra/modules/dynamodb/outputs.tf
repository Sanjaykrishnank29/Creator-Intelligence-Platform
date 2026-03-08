output "creator_profiles_table_name" {
  value = aws_dynamodb_table.creator_profiles.name
}

output "creator_content_table_name" {
  value = aws_dynamodb_table.creator_content.name
}

output "predictions_table_name" {
  value = aws_dynamodb_table.predictions.name
}

output "trend_signals_table_name" {
  value = aws_dynamodb_table.trend_signals.name
}

output "llm_cache_table_name" {
  value = aws_dynamodb_table.llm_cache.name
}
