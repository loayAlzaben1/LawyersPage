<#
Usage:
  - Ensure GitHub CLI (gh) is installed and authenticated: `gh auth login`
  - From repository root run (replace values):
      .\scripts\set_github_secrets.ps1 -RepoOwner "your-org-or-user" -RepoName "repo-name" -DbName "ci_db" -DbUser "ci_user" -DbPass "supersecret"

This script will set three repository secrets: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
#>

param(
  [string]$RepoOwner,
  [string]$RepoName,
  [string]$DbName,
  [string]$DbUser,
  [string]$DbPass
)

if (-not $RepoOwner -or -not $RepoName) {
  Write-Error "Please supply -RepoOwner and -RepoName"
  exit 1
}

$repo = "$RepoOwner/$RepoName"

Write-Host "Setting secrets for repository: $repo"

gh secret set POSTGRES_DB --body $DbName --repo $repo
gh secret set POSTGRES_USER --body $DbUser --repo $repo
gh secret set POSTGRES_PASSWORD --body $DbPass --repo $repo

Write-Host "Done. Verify secrets in repository settings -> Secrets -> Actions."
