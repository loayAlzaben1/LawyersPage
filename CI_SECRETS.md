## Setting GitHub Secrets for CI (Postgres)

To run the `postgres-test` job securely, add the following repository secrets in GitHub:

- `POSTGRES_DB` - database name used by the CI Postgres service
- `POSTGRES_USER` - username
- `POSTGRES_PASSWORD` - password

Easiest way (recommended): use the GitHub CLI and the provided helper script.

Example (PowerShell):

```powershell
# Authenticate first:
gh auth login

# Run script (replace placeholders):
.\scripts\set_github_secrets.ps1 -RepoOwner "your-user-or-org" -RepoName "repo" -DbName "ci_db" -DbUser "ci_user" -DbPass "supersecret"
```

Alternatively you can add them by visiting: `https://github.com/<owner>/<repo>/settings/secrets/actions`

Bash (Linux/macOS) helper

The repository includes a cross-platform Bash helper `scripts/set_github_secrets.sh` which supports reading from a `.env` file or prompting interactively (password input is hidden):

Example usages:

```bash
# Interactive prompts:
./scripts/set_github_secrets.sh -o your-org -r repo-name

# Provide an env file with POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
./scripts/set_github_secrets.sh -o your-org -r repo-name --env-file .env

# or pass values directly (less recommended because the password may appear in shell history):
./scripts/set_github_secrets.sh -o your-org -r repo-name -d ci_db -u ci_user -p supersecret
```

Security note: Prefer using `--env-file` (with file permissions restricted) or the interactive prompt to avoid exposing credentials in shell history. Also ensure the user running the script has push/write access to the repository.

Making the Bash script executable (Linux/macOS)

From the repository root you can run:

```bash
# Make script executable locally
chmod +x scripts/set_github_secrets.sh

# (Optional) Persist the executable bit in git so others get it too
git add scripts/set_github_secrets.sh
git commit -m "Make GH secrets helper executable"
git push
```

Or use the provided Makefile target (requires make):

```bash
make prepare-scripts
```

Note: On Windows (PowerShell) the `.ps1` script does not need an executable bit; run it with PowerShell directly.

Enable the repo pre-commit hooks (optional but recommended)

This repository includes a simple pre-commit hook in `.githooks/pre-commit` which will ensure any `scripts/*.sh` files are made executable and staged with the executable bit.

To enable it locally:

```bash
# Configure your repository to use the bundled hooks
git config core.hooksPath .githooks

# Or run the make helper
make enable-githooks
```

You only need to run this once per local clone. The hook will run on each commit and adjust file modes automatically.

Using the official pre-commit framework (recommended)

This repository also includes a `.pre-commit-config.yaml` which provides a local hook `ensure-scripts-executable` that will make `scripts/*.sh` executable and stage them.

Install and enable pre-commit hooks:

```bash
# Install pre-commit (if not already installed)
pip install --user pre-commit

# Install hooks for this repository
pre-commit install

# Optionally run the hooks once against all files
pre-commit run --all-files
```

You can also use the Make helper:

```bash
make install-precommit
```

