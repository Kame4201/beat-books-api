#!/usr/bin/env bash
# set-branch-protection.sh
# Configures branch protection rules for the main branch via GitHub API.
# Requires: gh CLI authenticated with a token that has repo admin permissions.
#
# Usage:
#   bash scripts/set-branch-protection.sh

set -euo pipefail

REPO="Kame4201/beat-books-api"
BRANCH="main"

echo "Configuring branch protection for ${REPO}:${BRANCH}..."

gh api \
  --method PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --header "Accept: application/vnd.github+json" \
  --field "required_status_checks[strict]=true" \
  --field "required_status_checks[contexts][]=lint" \
  --field "required_status_checks[contexts][]=test" \
  --field "enforce_admins=false" \
  --field "required_pull_request_reviews[required_approving_review_count]=1" \
  --field "required_pull_request_reviews[dismiss_stale_reviews]=false" \
  --field "required_pull_request_reviews[require_code_owner_reviews]=false" \
  --field "restrictions=null"

echo "Branch protection rules applied successfully."
echo ""
echo "Rules configured:"
echo "  - Require at least 1 approving review before merging"
echo "  - Require status checks: lint, test"
echo "  - Require branches to be up to date with main before merging (strict=true)"
