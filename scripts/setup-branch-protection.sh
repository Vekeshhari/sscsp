#!/usr/bin/env bash
# Enables branch protection on main and develop.
# Requires: gh CLI authenticated (gh auth login)

set -euo pipefail
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

for BRANCH in main develop; do
  echo "Protecting $BRANCH of $REPO..."
  gh api -X PUT "repos/$REPO/branches/$BRANCH/protection" \
    -H "Accept: application/vnd.github+json" \
    -f required_status_checks='{"strict":true,"contexts":["build-test-secure"]}' \
    -f enforce_admins=true \
    -f required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
    -f restrictions=null \
    -f allow_force_pushes=false \
    -f allow_deletions=false \
    -f required_linear_history=true
  echo "  ✔ $BRANCH protected"
done
