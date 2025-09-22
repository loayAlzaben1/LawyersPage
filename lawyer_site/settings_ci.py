from .settings import *
import os
from pathlib import Path

# Ensure BASE_DIR is defined (fallback to project root)
if 'BASE_DIR' not in globals():
    BASE_DIR = Path(__file__).resolve().parent.parent

# By default use SQLite for speed. Allow switching to Postgres in CI by setting CI_USE_POSTGRES=1
if os.environ.get('CI_USE_POSTGRES') == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'NAME': os.environ.get('POSTGRES_DB', 'ci_db'),
            'USER': os.environ.get('POSTGRES_USER', 'ci_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(Path(BASE_DIR) / 'ci.sqlite3'),
        }
    }

# Avoid heavy static collection in CI
COLLECTSTATIC = False
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Disable emails in CI
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Use a predictable media directory inside the repo so we can remove it at the end
MEDIA_ROOT = str(Path(BASE_DIR) / 'ci_media')
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Keep secret key from main settings but ensure DEBUG is False for parity
DEBUG = False
