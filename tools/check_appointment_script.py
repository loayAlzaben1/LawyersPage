import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()
from django.test import Client

def main():
    c = Client()
    r = c.get('/appointment/?service=consultations', SERVER_NAME='127.0.0.1', HTTP_HOST='127.0.0.1')
    print('status', r.status_code)
    txt = r.content.decode('utf-8')
    # Print a short tail of the HTML so we can inspect whether the JS block exists
    tail = txt[-2000:]
    print('--- tail ---')
    print(tail)
    found = 'URLSearchParams' in txt or 'nameInput.focus' in txt or 'form.scrollIntoView' in txt
    print('\nautofocus script present:', found)
    return 0

if __name__ == '__main__':
    sys.exit(main())
