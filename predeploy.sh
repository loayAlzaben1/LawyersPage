#!/usr/bin/env sh
set -e

TRIES=0
MAX=24
SLEEP=5

echo "Waiting for database..."
until python manage.py showmigrations > /dev/null 2>&1 || [ "$TRIES" -ge "$MAX" ]; do
  TRIES=$((TRIES+1))
  echo "DB not ready yet (try $TRIES/$MAX). Sleeping ${SLEEP}s..."
  sleep $SLEEP
done

if [ "$TRIES" -ge "$MAX" ]; then
  echo "Database not ready after $((MAX * SLEEP))s"
  exit 1
fi

echo "Running migrations..."
python manage.py migrate || {
  echo "migrate failed, retrying once..."
  sleep 3
  python manage.py migrate
}

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "collectstatic failed; continuing"

echo "Pre-deploy finished."
