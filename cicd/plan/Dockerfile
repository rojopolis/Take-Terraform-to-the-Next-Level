FROM hashicorp/terraform:0.12.6

LABEL "com.github.actions.name"="Custom Terraform plan"
LABEL "com.github.actions.description"="Run terraform plan"
LABEL "com.github.actions.icon"="book-open"
LABEL "com.github.actions.color"="purple"

LABEL "repository"="https://github.com/rojopolis/Take-Terraform-to-the-Next-Level"
LABEL "homepage"="https://github.com/rojopolis/Take-Terraform-to-the-Next-Level"
LABEL "maintainer"="rojopolis"

RUN apk --no-cache add jq curl python3

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]