resource "aws_s3_bucket" "raw_trends" {
  bucket = "${var.project_name}-${var.environment}-raw-trends"

  tags = {
    Environment = var.environment
    Name        = "RawTrendsBucket"
  }
}

resource "aws_s3_bucket" "dataset" {
  bucket = "${var.project_name}-${var.environment}-dataset"

  tags = {
    Environment = var.environment
    Name        = "DatasetBucket"
  }
}

resource "aws_s3_bucket" "static_website" {
  bucket = "${var.project_name}-${var.environment}-static-website"

  tags = {
    Environment = var.environment
    Name        = "StaticWebsiteBucket"
  }
}

resource "aws_s3_bucket_website_configuration" "static_website_config" {
  bucket = aws_s3_bucket.static_website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "static_website_pab" {
  bucket = aws_s3_bucket.static_website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "static_website_policy" {
  bucket = aws_s3_bucket.static_website.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.static_website.arn}/*"
      },
    ]
  })
  
  depends_on = [aws_s3_bucket_public_access_block.static_website_pab]
}
