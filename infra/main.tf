# One IAM role that GitHub Actions in this repo can assume with OIDC.
# It can do exactly one thing: ask Amazon Inspector to scan an SBOM.

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

# GitHub's OIDC subject for this repo, in its immutable form (owner and repo with their numeric IDs).
# Find yours with: gh api repos/OWNER/REPO/actions/oidc/customization/sub --jq .sub_claim_prefix
variable "github_sub_prefix" {
  description = "sub_claim_prefix of the GitHub repo allowed to use this role"
  type        = string
  default     = "repo:dkojo@167027053/devsecops-github-actions@1466137351"
}

# The GitHub OIDC provider already exists in the account (created for project 1)
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    # Only runs on main and on pull requests in this repo
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["${var.github_sub_prefix}:ref:refs/heads/main", "${var.github_sub_prefix}:pull_request"]
    }
  }
}

resource "aws_iam_role" "inspector_scan" {
  name               = "github-devsecops-inspector-scan"
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

resource "aws_iam_role_policy" "inspector_scan" {
  name = "inspector-scan-sbom"
  role = aws_iam_role.inspector_scan.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "inspector-scan:ScanSbom", Resource = "*" }]
  })
}

output "role_arn" {
  description = "Save this as the AWS_ROLE_ARN secret in GitHub"
  value       = aws_iam_role.inspector_scan.arn
}
