terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  full_name = "${var.project_name}-${var.environment}"
}

# Package the Lambda from the repo root (one level up from infra/)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/.."
  output_path = "${path.module}/build/lambda.zip"

  excludes = [
    ".git",
    ".github",
    "infra",
    "build",
    "__pycache__",
    "*.pyc",
    ".venv",
    "venv",
  ]
}

# IAM role for Lambda
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${locals.full_name}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    sid     = "AllowLogs"
    effect  = "Allow"
    actions = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }

  statement {
    sid    = "AllowBedrock"
    effect = "Allow"

    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "AllowOpenSearch"
    effect = "Allow"

    actions = [
      "es:ESHttpGet",
      "es:ESHttpPost",
      "es:ESHttpPut",
    ]

    resources = [var.opensearch_arn]
  }
}

resource "aws_iam_role_policy" "lambda_role_policy" {
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${locals.full_name}-lambda"
  retention_in_days = 14
}

resource "aws_lambda_function" "ai_search" {
  function_name = "${locals.full_name}-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  timeout     = 30
  memory_size = 1024

  environment {
    variables = {
      BEDROCK_MODEL_ID = var.bedrock_model_id
      AWS_REGION       = var.aws_region
      OPENSEARCH_HOST  = var.opensearch_host
    }
  }
}

# Public HTTP API (no auth) ------------------------

resource "aws_apigatewayv2_api" "public_api" {
  name          = "${locals.full_name}-public-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "public_integration" {
  api_id                 = aws_apigatewayv2_api.public_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.ai_search.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "public_route" {
  api_id    = aws_apigatewayv2_api.public_api.id
  route_key = "POST /ai-search"
  target    = "integrations/${aws_apigatewayv2_integration.public_integration.id}"
}

resource "aws_apigatewayv2_stage" "public_stage" {
  api_id      = aws_apigatewayv2_api.public_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "public_apigw_invoke" {
  statement_id  = "AllowPublicAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_search.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.public_api.execution_arn}/*/*"
}

# Private HTTP API (IAM-authenticated) -------------

resource "aws_apigatewayv2_api" "private_api" {
  name          = "${locals.full_name}-private-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "private_integration" {
  api_id                 = aws_apigatewayv2_api.private_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.ai_search.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "private_route" {
  api_id             = aws_apigatewayv2_api.private_api.id
  route_key          = "POST /ai-search"
  target             = "integrations/${aws_apigatewayv2_integration.private_integration.id}"
  authorization_type = "AWS_IAM"
}

resource "aws_apigatewayv2_stage" "private_stage" {
  api_id      = aws_apigatewayv2_api.private_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "private_apigw_invoke" {
  statement_id  = "AllowPrivateAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_search.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.private_api.execution_arn}/*/*"
}

output "public_invoke_url" {
  description = "Public endpoint URL (no auth)"
  value       = "${aws_apigatewayv2_api.public_api.api_endpoint}/ai-search"
}

output "private_invoke_url" {
  description = "Private endpoint URL (AWS_IAM auth)"
  value       = "${aws_apigatewayv2_api.private_api.api_endpoint}/ai-search"
}

