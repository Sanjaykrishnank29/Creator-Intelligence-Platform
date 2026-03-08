output "raw_trends_bucket_name" {
  value = aws_s3_bucket.raw_trends.bucket
}

output "dataset_bucket_name" {
  value = aws_s3_bucket.dataset.bucket
}

output "static_website_bucket_name" {
  value = aws_s3_bucket.static_website.bucket
}

output "static_website_endpoint" {
  value = aws_s3_bucket_website_configuration.static_website_config.website_endpoint
}
