import sys
from django.conf import settings

_logged_init = False

class LogHostMiddleware:
    """Temporary middleware for debugging ALLOWED_HOSTS and request Host header.

    It prints the current settings.ALLOWED_HOSTS once per process and logs
    the incoming request.get_host() for each request. Output is sent to
    stderr so it appears in container logs.
    """

    def __init__(self, get_response):
        global _logged_init
        self.get_response = get_response
        if not _logged_init:
            try:
                print(f"[middleware] ALLOWED_HOSTS at init: {settings.ALLOWED_HOSTS}", file=sys.stderr)
            except Exception as e:
                print(f"[middleware] failed to read ALLOWED_HOSTS: {e}", file=sys.stderr)
            _logged_init = True

    def __call__(self, request):
        try:
            host = request.get_host()
        except Exception as e:
            print(f"[middleware] request.get_host() raised: {e}", file=sys.stderr)
            raise
        print(f"[middleware] request host: {host}", file=sys.stderr)
        return self.get_response(request)
