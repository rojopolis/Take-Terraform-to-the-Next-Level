terraform {
  required_version = ">= 0.11.8"
  backend "s3" {
    bucket         = "my90-tf"
    key            = "my90-api-gateway-deployment"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals { 
    aws_region       = "${data.aws_region.current.name}"
    environment_slug = "${lower(terraform.workspace)}" # TODO: force this to conform to API GW naming restrictions
}

data "terraform_remote_state" "gateway_rest_api" {
  backend = "s3"
  workspace = "${var.environment}"
  config {
    bucket         = "my90-tf"
    key            = "my90-api-gateway-rest-api"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

data "terraform_remote_state" "lambda" {
  backend = "s3"
  workspace = "${terraform.workspace}"
  config {
    bucket         = "my90-tf"
    key            = "my90-api-lambda"
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

resource "aws_api_gateway_deployment" "my90_api_gateway_deployment" {
    rest_api_id       = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_id}"
    description       = "${local.environment_slug}"
    stage_name        = "${local.environment_slug}"
    stage_description = "${local.environment_slug}"
    depends_on        = ["aws_lambda_permission.crud_handler_lambda_permission"]
}

resource "aws_lambda_permission" "crud_handler_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "${data.terraform_remote_state.lambda.crud_handler_lambda_arn}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_execution_arn}/*/*/*"
}