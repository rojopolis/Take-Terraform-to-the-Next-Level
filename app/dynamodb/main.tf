terraform {
  required_version = ">= 0.11.8"
  backend "s3" {
    bucket         = "my90-tf"
    key            = "my90-api-dynamodb"
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

resource "random_id" "random_suffix" {
  byte_length = 8
}

resource "aws_dynamodb_table" "agencies_table" {
  name           = "agencies-${random_id.random_suffix.hex}"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "Partition"
  range_key      = "Sort"

  attribute {
    name = "Partition"
    type = "S"
  }

  attribute {
      name = "Sort"
      type = "S"
  }

  attribute {
      name = "LSI"
      type = "S"
  }

  local_secondary_index {
    name = "ParentIdIndex"
    range_key = "LSI"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "producer_table" {
  name           = "producer-${random_id.random_suffix.hex}"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "AgencyId"
  range_key      = "SurveyId"

  attribute {
    name = "AgencyId"
    type = "S"
  }

  attribute {
      name = "SurveyId"
      type = "S"
  }
}
