workflow "Terraform" {
  resolves = ["Debug", "terraform-plan-cognito"]
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

action "terraform-fmt" {
  uses = "hashicorp/terraform-github-actions/fmt@v0.3.4"
  needs = "filter-to-pr-open-synced"
  secrets = ["GITHUB_TOKEN"]
  env = {
    TF_ACTION_WORKING_DIR = "app"
  }
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

action "terraform-workspace-cognito" {
  uses = "hashicorp/terraform-github-actions/plan@v0.3.4"
  needs = "terraform-validate-cognito"
  secrets = ["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  runs = ["sh", "-c", "cd $TF_ACTION_WORKING_DIR; terraform workspace select $GITHUB_HEAD_REF || terraform workspace new $GITHUB_HEAD_REF"]
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