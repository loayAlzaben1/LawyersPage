#!/usr/bin/env bash
set -euo pipefail

echo "pre-commit: ensuring scripts/*.sh are executable"
for f in scripts/*.sh; do
  if [ -f "$f" ] && [ ! -x "$f" ]; then
    chmod +x "$f"
    git add "$f"
    echo "Made executable and staged: $f"
  fi
done

exit 0
