workflow "Terraform" {
  resolves = "terraform-fmt"
  on = "push"
}

action "terraform-fmt" {
  uses = "hashicorp/terraform-github-actions/fmt@v0.3.4"
  args = "-recursive"
  secrets = ["GITHUB_TOKEN"]
  env = {
    TF_ACTION_WORKING_DIR = "."
  }
}