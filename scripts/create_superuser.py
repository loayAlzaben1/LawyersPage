"""
Create or update a Django superuser from environment variables.

Usage (non-interactive, recommended from VS Code terminal):

$env:SUPERUSER_USERNAME = 'admin'
$env:SUPERUSER_EMAIL = 'you@example.com'
$env:SUPERUSER_PASSWORD = 'S3cureP@ss!'
python scripts/create_superuser.py

This script will create the user if missing, set is_staff and is_superuser, and set the password.
If the required env vars are not provided the script will fall back to the interactive
`manage.py createsuperuser` command.

Security: avoid committing real passwords to files or git. Use environment variables.
"""

import os
import sys
import pathlib

# Ensure the project root (one level above this scripts/ folder) is on sys.path.
# When Python runs a script directly, sys.path[0] is the script's directory; that
# can prevent Django from finding the project package (e.g. `lawyer_site`). Add
# the project root so imports work whether you run this file directly or via
# the project root.
project_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')

try:
    import django
    django.setup()
except Exception as exc:
    print('Error setting up Django (are you running from the project root where manage.py lives?):', exc)
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

username = os.environ.get('SUPERUSER_USERNAME')
email = os.environ.get('SUPERUSER_EMAIL', '')
password = os.environ.get('SUPERUSER_PASSWORD')

if not username or not password:
    print('Environment variables SUPERUSER_USERNAME and SUPERUSER_PASSWORD not both set.')
    print('Falling back to interactive createsuperuser...')
    try:
        call_command('createsuperuser')
    except Exception as e:
        print('Error running createsuperuser:', e)
        sys.exit(1)
    sys.exit(0)

try:
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print(f"User '{username}' {'created' if created else 'updated'} and set as superuser.")
except Exception as e:
    print('Failed to create/update user:', e)
    sys.exit(1)
