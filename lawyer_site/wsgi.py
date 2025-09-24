import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
application = get_wsgi_application()
# Debug: print ALLOWED_HOSTS at WSGI startup to stderr so it's visible in container logs
try:
	import sys
	from django.conf import settings
	print(f"WSGI ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', None)}", file=sys.stderr)
except Exception:
	pass

# Optional: run migrations on WSGI startup if explicitly enabled (temporary safety net).
# Set RUN_MIGRATIONS_AT_STARTUP=1 in the environment to enable.
try:
	if os.getenv('RUN_MIGRATIONS_AT_STARTUP', '0') == '1':
		# Import and run migrations programmatically
		from django.core.management import call_command
		print('Running migrations at WSGI startup...', file=sys.stderr)
		call_command('migrate', '--noinput')
		print('Migrations complete.', file=sys.stderr)
except Exception as e:
	# Log but don't crash the WSGI startup
	try:
		print(f'Error running migrations at WSGI startup: {e}', file=sys.stderr)
	except Exception:
		pass
