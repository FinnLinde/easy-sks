resource "aws_cognito_user_pool" "main" {
  name = var.project_name

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 7
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_domain" "hosted_ui" {
  count = var.cognito_domain_prefix == null ? 0 : 1

  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.main.id
}

# ---------------------------------------------------------------------------
# App clients
# ---------------------------------------------------------------------------

resource "aws_cognito_user_pool_client" "prod" {
  name         = "${var.project_name}-prod"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  callback_urls = var.prod_callback_urls
  logout_urls   = var.prod_logout_urls

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]

  access_token_validity  = 1  # hours
  id_token_validity      = 1  # hours
  refresh_token_validity = 30 # days

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_user_pool_client" "local_dev" {
  name         = "${var.project_name}-local-dev"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]

  callback_urls = var.dev_callback_urls
  logout_urls   = var.dev_logout_urls

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]

  access_token_validity  = 24 # hours
  id_token_validity      = 24 # hours
  refresh_token_validity = 30 # days

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "LEGACY"
}

# ---------------------------------------------------------------------------
# User groups (mapped to backend Role enum)
# ---------------------------------------------------------------------------

resource "aws_cognito_user_group" "freemium" {
  name         = "freemium"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Free-tier users"
}

resource "aws_cognito_user_group" "premium" {
  name         = "premium"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Premium subscribers"
}

resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Administrators"
}
