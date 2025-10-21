#!/usr/bin/env bash
# Simple deploy helper for PythonAnywhere
# Usage: run from your PythonAnywhere Bash console after cloning the repo to ~/yourproject

set -euo pipefail
PROJECT_DIR="$HOME/yourproject"
VENV_DIR="$HOME/venvs/lawyerspage"
BRANCH="feature/add-static-root"

echo "Activating venv: $VENV_DIR"
source "$VENV_DIR/bin/activate"

cd "$PROJECT_DIR"

echo "Fetching latest from origin and checking out $BRANCH"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

echo "Installing requirements (may take a while)"
pip install -r requirements.txt

echo "Running migrations"
python manage.py migrate --noinput

echo "Collecting static files"
python manage.py collectstatic --noinput

echo "Restarting web app (you may need to reload from the PythonAnywhere Web tab)"
# Try to reload via PythonAnywhere helper (if available)
if command -v pa_reload_webapp >/dev/null 2>&1; then
  pa_reload_webapp
else
  echo "pa_reload_webapp command not available; please reload the web app from the PythonAnywhere Web tab."
fi

echo "Deploy complete."