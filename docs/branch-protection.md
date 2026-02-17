# Branch Protection Rules — `main`

This document describes the branch protection rules configured for the `main` branch and how to apply them.

## Rules

| Rule | Setting |
|------|---------|
| Required approving reviews | 1 |
| Dismiss stale reviews | No |
| Require status checks to pass | Yes |
| Required status checks | `lint`, `test` |
| Require branch to be up to date | Yes (strict mode) |
| Enforce for administrators | No |

## Status Checks

The following GitHub Actions jobs must pass before a PR can be merged:

- **`lint`** — defined in `.github/workflows/lint.yml` (runs `ruff` and `black`)
- **`test`** — defined in `.github/workflows/test.yml` (runs `pytest` with coverage)

## Applying the Rules

Branch protection rules are GitHub repository settings and must be configured via the GitHub API or UI. They cannot be stored as a file in the repository.

### Option 1: Script (Recommended)

Use the provided script with the `gh` CLI:

```bash
# Authenticate gh CLI (if not already done)
gh auth login

# Run the script
bash scripts/set-branch-protection.sh
```

The script requires a GitHub token with `repo` admin permissions.

### Option 2: GitHub UI

1. Go to **Settings → Branches** in this repository.
2. Click **Add rule** (or edit the existing `main` rule).
3. Configure:
   - **Branch name pattern**: `main`
   - Check **Require a pull request before merging**
     - Set **Required approvals** to `1`
   - Check **Require status checks to pass before merging**
     - Check **Require branches to be up to date before merging**
     - Search for and add: `lint`, `test`
4. Click **Create** or **Save changes**.

### Option 3: GitHub API (curl)

```bash
curl -X PUT \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Kame4201/beat-books-api/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["lint", "test"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": false,
      "require_code_owner_reviews": false
    },
    "restrictions": null
  }'
```

## Notes

- The `gh` CLI token used in CI (Actions) may not have admin permissions to set branch protection. Run the script locally or use the UI.
- Status check names (`lint`, `test`) must exactly match the `jobs.<job-id>` keys in the workflow YAML files.
- Branch protection rules are not enforced retroactively on open PRs — they apply to new merge attempts after the rule is saved.
