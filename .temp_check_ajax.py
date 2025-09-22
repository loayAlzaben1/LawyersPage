import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from django.test import Client
c = Client()
resp = c.get('/blog/page/?page=2', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
print('ajax status', resp.status_code)
print('content (start):', resp.content[:200])
