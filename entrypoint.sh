#!/bin/sh
set -e

# Basic entrypoint: run migrations, collectstatic, then start gunicorn
cd /app

# attempt migrations (may fail if DB not ready)
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

exec gunicorn lawyer_site.wsgi:application --bind 0.0.0.0:8000
