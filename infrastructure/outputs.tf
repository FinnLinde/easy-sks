output "user_pool_id" {
  description = "Cognito User Pool ID (maps to AUTH_COGNITO_USER_POOL_ID)"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_region" {
  description = "AWS region of the User Pool (maps to AUTH_COGNITO_REGION)"
  value       = var.aws_region
}

output "prod_client_id" {
  description = "App client ID for production (maps to AUTH_COGNITO_APP_CLIENT_ID)"
  value       = aws_cognito_user_pool_client.prod.id
}

output "dev_client_id" {
  description = "App client ID for local development (maps to AUTH_COGNITO_APP_CLIENT_ID)"
  value       = aws_cognito_user_pool_client.local_dev.id
}

output "cognito_hosted_ui_domain" {
  description = "Hosted UI base URL for frontend NEXT_PUBLIC_COGNITO_DOMAIN (null if cognito_domain_prefix is unset)"
  value = (
    length(aws_cognito_user_pool_domain.hosted_ui) > 0
    ? "https://${aws_cognito_user_pool_domain.hosted_ui[0].domain}.auth.${var.aws_region}.amazoncognito.com"
    : null
  )
}
