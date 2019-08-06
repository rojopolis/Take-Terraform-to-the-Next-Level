terraform {
  required_version = ">= 0.11.8"
  backend "s3" {
    bucket         = "my90-tf"
    key            = "my90-api-gateway-artifacts"
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
    aws_region       = "${data.aws_region.current.name}"
    environment_slug = "${lower(terraform.workspace)}" # TODO: force this to conform to API GW naming restrictions
}

data "terraform_remote_state" "gateway_rest_api" {
  backend = "s3"
  workspace = "default"
  config {
    bucket         = "my90-tf"
    key            = "my90-api-gateway-rest-api"
    region         = "us-east-1"
    dynamodb_table = "my90-terraform-lock"
  }
}

module "aws_api_gateway_sdk_archive" {
  source         = "rojopolis/api-gateway-sdk-archive/aws"
  version        = "0.1.1"
  api_gateway_id = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_id}"
  stage_name     = "${local.environment_slug}"
  sdk_type       = "javascript"
  archive_file   = "${path.module}/my90-api-${local.environment_slug}.zip"
}

resource "aws_s3_bucket_object" "aws_api_gateway_sdk_archive_object" {
  bucket     = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_bucket}"
  key        = "my90-api-${local.environment_slug}.zip"
  source     = "${module.aws_api_gateway_sdk_archive.archive_file}"
  acl        = "public-read"
  depends_on = ["module.aws_api_gateway_sdk_archive"]
}

module "aws_api_gateway_export" {
  source          = "rojopolis/api-gateway-export/aws"
  version         = "0.1.5"
  api_gateway_id  = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_id}"
  stage_name      = "${local.environment_slug}"
  region          = "${local.aws_region}"
  extensions      = "postman"
  format          = "json"
  openapi_version = "swagger"
}

resource "aws_s3_bucket_object" "aws_api_gateway_export_object" {
  bucket     = "${data.terraform_remote_state.gateway_rest_api.my90_rest_api_bucket}"
  key        = "my90-api-${local.environment_slug}.json"
  content    = "${module.aws_api_gateway_export.api_export}"
  acl        = "public-read"
}