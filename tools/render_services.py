import os
import sys

# Ensure project root is on sys.path so Django settings package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()

from django.test import Client

def main():
    c = Client()
    # Use a valid host header so ALLOWED_HOSTS doesn't reject the test-client request
    resp = c.get('/services/', SERVER_NAME='127.0.0.1', HTTP_HOST='127.0.0.1')
    print('status:', resp.status_code)
    text = resp.content.decode('utf-8')
    marker = '<script type="application/ld+json">'
    i = text.find(marker)
    if i == -1:
        print('JSON-LD block not found')
        return 1
    snippet = text[i:text.find('</script>', i)+9]
    print('--- JSON-LD snippet (truncated) ---')
    print(snippet[:2000])
    return 0

if __name__ == '__main__':
    sys.exit(main())
