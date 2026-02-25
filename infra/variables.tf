variable "project_name" {
  type        = string
  default     = "ai-search-gateway"
  description = "Base name for Lambda, API, etc."
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev | qa | prod)."
  default     = "dev"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for Lambda, Bedrock, and API Gateway."
}

variable "bedrock_model_id" {
  type        = string
  description = "Bedrock Claude Sonnet model ID."
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "opensearch_host" {
  type        = string
  description = "OpenSearch/Elasticsearch endpoint (e.g. https://domain.region.es.amazonaws.com)."
}

variable "opensearch_arn" {
  type        = string
  description = "ARN of the OpenSearch domain for IAM policy."
}

