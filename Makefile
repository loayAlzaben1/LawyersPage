.PHONY: prepare-scripts

prepare-scripts:
	@echo "Making helper scripts executable"
	chmod +x scripts/set_github_secrets.sh || true
	powershell -Command "if (Test-Path scripts/set_github_secrets.ps1) { Write-Host 'PowerShell script present (no chmod needed on Windows).' }"
	@echo "Done. You can now run ./scripts/set_github_secrets.sh on Linux/macOS"

.PHONY: enable-githooks
enable-githooks:
	@echo "Setting local git hooks path to .githooks for this repo"
	@git config core.hooksPath .githooks
	@echo "Done. pre-commit hooks will now run automatically."

.PHONY: install-precommit
install-precommit:
	@echo "Installing pre-commit hooks (requires Python and pre-commit package)"
	@pip install --user pre-commit || true
	@pre-commit install || true
	@echo "pre-commit installed"

.PHONY: fix-style
fix-style:
	@echo "Running ruff --fix and black ."
	@ruff --fix . || true
	@black . || true
	@echo "Style fixes applied (stage changes and commit as needed)"
