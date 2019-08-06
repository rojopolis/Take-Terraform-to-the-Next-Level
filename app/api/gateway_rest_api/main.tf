terraform {
  required_version = ">= 0.11.8"
  backend "s3" {
    bucket         = "my90-tf"
    key            = "my90-api-gateway-rest-api"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

provider "aws" {
    version = "~> 1.39"
    assume_role {
      role_arn     = "${var.aws_role_arn}"
    }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals { 
    aws_account_id   = "${var.aws_account_id}"
    aws_region       = "${data.aws_region.current.name}"
    environment_slug = "${var.git_branch}"
}

data "terraform_remote_state" "lambda" {
  backend = "s3"
  workspace = "${local.environment_slug}"
  config {
    bucket         = "my90-tf"
    key            = "my90-api-lambda"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

data "terraform_remote_state" "cognito_user_pool" {
  backend = "s3"
  workspace = "${terraform.workspace}"
  config {
    bucket         = "my90-tf"
    key            = "my90-api-cognito-user-pool"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

data "template_file" "swagger_json" {
  template = "${file("${path.module}/../swagger.json")}"
  vars {
    crud_handler_lambda_qualified_arn = "${data.terraform_remote_state.lambda.crud_handler_lambda_qualified_arn}"
    my90_user_pool_arn                = "${data.terraform_remote_state.cognito_user_pool.my90_user_pool_arn}"
    my90_user_pool_resource_server_identifier = "${data.terraform_remote_state.cognito_user_pool.my90_user_pool_resource_server_identifier}"
  }
}

resource "aws_api_gateway_rest_api" "my90_api" {
  name        = "My90 API"
  description = "My90 API"
  body        = "${data.template_file.swagger_json.rendered}"
}

resource "aws_api_gateway_authorizer" "my90_user_pool" {
  name                   = "my90-authorizer"
  rest_api_id            = "${aws_api_gateway_rest_api.my90_api.id}"
  type                   = "COGNITO_USER_POOLS"
  provider_arns          = ["${data.terraform_remote_state.cognito_user_pool.my90_user_pool_arn}"]
}