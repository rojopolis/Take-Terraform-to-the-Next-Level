terraform {
  required_version = ">= 0.11.8"
  backend "s3" {
    bucket         = "my90-tf"
    key            = "my90-api-cloudwatch"
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

resource "aws_cloudwatch_event_rule" "producer_timer" {
  name                = "producer-timer-${local.environment_slug}"
  description         = "Execute producer Lambda"
  schedule_expression = "rate(${var.poll_interval} minutes)"
}

resource "aws_cloudwatch_event_target" "producer_target" {
  rule      = "${aws_cloudwatch_event_rule.producer_timer.name}"
  arn       = "${data.terraform_remote_state.lambda.producerjobs_handler_lambda_arn}"
}

resource "aws_lambda_permission" "producerjobs_handler_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "${data.terraform_remote_state.lambda.producerjobs_handler_lambda_arn}"
  principal     = "events.amazonaws.com"

  source_arn = "arn:aws:events:${local.aws_region}:${local.aws_account_id}:rule/*"
}