workflow "Terraform" {
  resolves = ["terraform-plan-lambda"]
  on = "pull_request"
}

action "Debug" {
  uses = "actions/bin/sh@master"
  args = ["env"]
}

action "filter-to-pr-open-synced" {
  uses = "actions/bin/filter@master"
  args = "action 'opened|synchronize'"
}

action "terraform-init-cognito" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = "filter-to-pr-open-synced"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cognito/user_pool"
  }
}

action "terraform-validate-cognito" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-cognito"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cognito/user_pool"
  }
}

action "terraform-plan-cognito" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-cognito"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

  env = {
    TF_ACTION_WORKING_DIR = "app/cognito/user_pool"
  }
}

action "terraform-init-dynamodb" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = "filter-to-pr-open-synced"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/dynamodb"
  }
}

action "terraform-validate-dynamodb" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-dynamodb"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/dynamodb"
  }
}

action "terraform-workspace-dynamodb" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-dynamodb"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
  env = {
    TF_ACTION_WORKING_DIR = "app/dynamodb"
  }
}

action "terraform-plan-dynamodb" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-dynamodb"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

  env = {
    TF_ACTION_WORKING_DIR = "app/dynamodb"
  }
}

action "terraform-init-sqs" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = "filter-to-pr-open-synced"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/sqs"
  }
}

action "terraform-validate-sqs" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-sqs"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/sqs"
  }
}

action "terraform-workspace-sqs" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-sqs"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
  env = {
    TF_ACTION_WORKING_DIR = "app/sqs"
  }
}

action "terraform-plan-sqs" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-sqs"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

  env = {
    TF_ACTION_WORKING_DIR = "app/sqs"
  }
}

action "terraform-init-kms" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = "filter-to-pr-open-synced"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/kms"
  }
}

action "terraform-validate-kms" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-kms"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/kms"
  }
}

action "terraform-workspace-kms" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-kms"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
  env = {
    TF_ACTION_WORKING_DIR = "app/kms"
  }
}

action "terraform-plan-kms" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-kms"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

  env = {
    TF_ACTION_WORKING_DIR = "app/kms"
  }
}

action "terraform-init-lambda" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = ["terraform-plan-kms", "terraform-plan-dynamodb", "terraform-plan-sqs", "terraform-plan-cognito",]
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/lambda"
  }
}

action "terraform-validate-lambda" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-lambda"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/lambda"
  }
}

action "terraform-workspace-lambda" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-lambda"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
  env = {
    TF_ACTION_WORKING_DIR = "app/lambda"
  }
}

action "terraform-plan-lambda" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-lambda"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/lambda"
  }
}

action "terraform-init-cloudwatch" {
  uses = "hashicorp/terraform-github-actions/init@v0.3.4"
  needs = ["terraform-plan-lambda"]
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cloudwatch"
  }
}

action "terraform-validate-cloudwatch" {
  uses = "hashicorp/terraform-github-actions/validate@v0.3.4"
  needs = "terraform-init-cloudwatch"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cloudwatch"
  }
}

action "terraform-workspace-cloudwatch" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-cloudwatch"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cloudwatch"
  }
}

action "terraform-plan-cloudwatch" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-cloudwatch"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  env = {
    TF_ACTION_WORKING_DIR = "app/cloudwatch"
  }
}