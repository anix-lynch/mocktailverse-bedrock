# Terraform Configuration for Mocktailverse GenAI Platform
# Provider: AWS (us-west-2)
# Services: Lambda, DynamoDB, S3, API Gateway, IAM, CloudFront

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "mocktailverse"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "prod"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 Buckets
resource "aws_s3_bucket" "raw" {
  bucket = "${var.project_name}-raw-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "${var.project_name}-raw"
    Environment = var.environment
    Purpose     = "Raw cocktail data storage"
  }
}

resource "aws_s3_bucket" "embeddings" {
  bucket = "${var.project_name}-embeddings-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "${var.project_name}-embeddings"
    Environment = var.environment
    Purpose     = "Vector embeddings storage"
  }
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "${var.project_name}-frontend"
    Environment = var.environment
    Purpose     = "Next.js static site"
  }
}

# S3 bucket configurations
resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "raw" {
  bucket = aws_s3_bucket.raw.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "embeddings" {
  bucket = aws_s3_bucket.embeddings.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Frontend bucket - public for CloudFront
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# DynamoDB Table
resource "aws_dynamodb_table" "metadata" {
  name           = "${var.project_name}-metadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "cocktail_id"

  attribute {
    name = "cocktail_id"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  global_secondary_index {
    name            = "NameIndex"
    hash_key        = "name"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "CategoryIndex"
    hash_key        = "category"
    projection_type = "ALL"
  }

  tags = {
    Name        = "${var.project_name}-metadata"
    Environment = var.environment
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-role"
  }
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.raw.arn,
          "${aws_s3_bucket.raw.arn}/*",
          aws_s3_bucket.embeddings.arn,
          "${aws_s3_bucket.embeddings.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.metadata.arn,
          "${aws_dynamodb_table.metadata.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-*"
      }
    ]
  })
}

# Lambda Functions
resource "aws_lambda_function" "ingest" {
  filename      = "${path.module}/../lambdas/ingest/deployment.zip"
  function_name = "${var.project_name}-ingest"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      RAW_BUCKET      = aws_s3_bucket.raw.id
      METADATA_TABLE  = aws_dynamodb_table.metadata.name
    }
  }

  tags = {
    Name = "${var.project_name}-ingest"
  }
}

resource "aws_lambda_function" "embed" {
  filename      = "${path.module}/../lambdas/embed/deployment.zip"
  function_name = "${var.project_name}-embed"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      METADATA_TABLE    = aws_dynamodb_table.metadata.name
      EMBEDDINGS_BUCKET = aws_s3_bucket.embeddings.id
    }
  }

  tags = {
    Name = "${var.project_name}-embed"
  }
}

resource "aws_lambda_function" "search" {
  filename      = "${path.module}/../lambdas/search/deployment.zip"
  function_name = "${var.project_name}-search"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      METADATA_TABLE = aws_dynamodb_table.metadata.name
    }
  }

  tags = {
    Name = "${var.project_name}-search"
  }
}

resource "aws_lambda_function" "rag" {
  filename      = "${path.module}/../lambdas/rag/deployment.zip"
  function_name = "${var.project_name}-rag"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      SEARCH_LAMBDA = aws_lambda_function.search.function_name
    }
  }

  tags = {
    Name = "${var.project_name}-rag"
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
  }

  tags = {
    Name = "${var.project_name}-api"
  }
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "prod"
  auto_deploy = true

  tags = {
    Name = "${var.project_name}-api-prod"
  }
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "search" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "rag" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# API Gateway integrations
resource "aws_apigatewayv2_integration" "search" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.search.invoke_arn
}

resource "aws_apigatewayv2_integration" "rag" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.rag.invoke_arn
}

# API Gateway routes
resource "aws_apigatewayv2_route" "search" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /v1/search"
  target    = "integrations/${aws_apigatewayv2_integration.search.id}"
}

resource "aws_apigatewayv2_route" "rag" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /v1/rag"
  target    = "integrations/${aws_apigatewayv2_integration.rag.id}"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend.website_endpoint
    origin_id   = "S3-${var.project_name}-frontend"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${var.project_name}-frontend"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "${var.project_name}-cloudfront"
  }
}

# EventBridge rule for scheduled ingestion
resource "aws_cloudwatch_event_rule" "daily_ingest" {
  name                = "${var.project_name}-daily-ingest"
  description         = "Trigger daily cocktail ingestion"
  schedule_expression = "cron(0 2 * * ? *)"  # 2 AM UTC daily

  tags = {
    Name = "${var.project_name}-daily-ingest"
  }
}

resource "aws_cloudwatch_event_target" "ingest" {
  rule      = aws_cloudwatch_event_rule.daily_ingest.name
  target_id = "IngestLambda"
  arn       = aws_lambda_function.ingest.arn

  input = jsonencode({
    fetch_type = "mocktails"
    limit      = 10
  })
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_ingest.arn
}

# Outputs
output "api_endpoint" {
  description = "API Gateway endpoint"
  value       = aws_apigatewayv2_stage.prod.invoke_url
}

output "cloudfront_url" {
  description = "CloudFront distribution URL"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "raw_bucket" {
  description = "S3 raw data bucket"
  value       = aws_s3_bucket.raw.id
}

output "frontend_bucket" {
  description = "S3 frontend bucket"
  value       = aws_s3_bucket.frontend.id
}

output "dynamodb_table" {
  description = "DynamoDB metadata table"
  value       = aws_dynamodb_table.metadata.name
}
