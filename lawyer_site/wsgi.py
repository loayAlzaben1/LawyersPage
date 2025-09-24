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
