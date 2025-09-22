"""Render blog index via Django test client and print whether placeholder is present for posts without images."""
import os
import sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()

from django.test import Client
from blog.models import BlogPost

client = Client()
# use a host that's allowed by default during development or add 'testserver' to ALLOWED_HOSTS
resp = client.get('/blog/', SERVER_NAME='localhost', HTTP_HOST='localhost')
print('status_code', resp.status_code)
html = resp.content.decode('utf-8')

# find a post without featured_image
missing = [p for p in BlogPost.objects.all() if not getattr(p, 'featured_image')]
print('posts without image:', [p.pk for p in missing])

if missing:
    placeholder = '/static/blog/img/placeholder-400x250.svg'
    found = placeholder in html
    print('placeholder path in HTML?', found)
    if not found:
        # also try {% static %} could resolve to the same path; print small snippet
        idx = html.find('placeholder-400x250')
        print('html snippet around placeholder:', html[max(0, idx-80):idx+80])
else:
    print('no posts missing images; nothing to check')
