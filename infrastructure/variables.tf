variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used as a prefix for resource naming"
  type        = string
  default     = "easy-sks"
}

variable "cognito_domain_prefix" {
  description = "Optional Cognito Hosted UI domain prefix (without .auth.<region>.amazoncognito.com)"
  type        = string
  default     = null
}

variable "prod_callback_urls" {
  description = "Allowed OAuth callback URLs for the production app client"
  type        = list(string)
}

variable "prod_logout_urls" {
  description = "Allowed OAuth logout URLs for the production app client"
  type        = list(string)
}

variable "dev_callback_urls" {
  description = "Allowed OAuth callback URLs for the local development app client"
  type        = list(string)
  default = [
    "http://localhost:3000",
    "http://localhost:3000/auth/callback",
  ]
}

variable "dev_logout_urls" {
  description = "Allowed OAuth logout URLs for the local development app client"
  type        = list(string)
  default     = ["http://localhost:3000"]
}
