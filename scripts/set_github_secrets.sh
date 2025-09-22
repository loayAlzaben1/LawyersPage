#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 -o owner -r repo [-d dbname] [-u dbuser] [-p dbpass] [--env-file .env]

If -d/-u/-p are omitted, the script will try to read them from the provided --env-file
or will prompt interactively. Password prompt is silent.
EOF
}

OWNER=""
REPO=""
DB=""
USER=""
PASS=""
ENV_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--owner)
      OWNER="$2"; shift 2;;
    -r|--repo)
      REPO="$2"; shift 2;;
    -d|--db)
      DB="$2"; shift 2;;
    -u|--user)
      USER="$2"; shift 2;;
    -p|--pass)
      PASS="$2"; shift 2;;
    --env-file)
      ENV_FILE="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -z "$OWNER" || -z "$REPO" ]]; then
  echo "owner and repo are required"
  usage
  exit 1
fi

if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -o allexport
  source "$ENV_FILE"
  set +o allexport
  : ${POSTGRES_DB:=${DB}}
  : ${POSTGRES_USER:=${USER}}
  : ${POSTGRES_PASSWORD:=${PASS}}
fi

if [[ -z "${POSTGRES_DB:-}" ]]; then
  read -rp "Postgres DB name: " POSTGRES_DB
fi

if [[ -z "${POSTGRES_USER:-}" ]]; then
  read -rp "Postgres user: " POSTGRES_USER
fi

if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
  read -rsp "Postgres password (input hidden): " POSTGRES_PASSWORD
  echo
fi

REPO_PATH="$OWNER/$REPO"

echo "Setting secrets for $REPO_PATH"
gh secret set POSTGRES_DB --body "$POSTGRES_DB" --repo "$REPO_PATH"
gh secret set POSTGRES_USER --body "$POSTGRES_USER" --repo "$REPO_PATH"
gh secret set POSTGRES_PASSWORD --body "$POSTGRES_PASSWORD" --repo "$REPO_PATH"

echo "Done. Verify in GitHub repository settings -> Secrets -> Actions"
