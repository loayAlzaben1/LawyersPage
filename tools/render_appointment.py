import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()
from django.test import Client

c = Client()
# pick a service if available
resp = c.get('/services/', SERVER_NAME='127.0.0.1', HTTP_HOST='127.0.0.1')
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.content, 'html.parser')
link = soup.select_one('a[href*="/appointment/?service="]')
if not link:
    print('No appointment link found on services page')
    sys.exit(1)
url = link['href']
print('Found link:', url)
resp2 = c.get(url, SERVER_NAME='127.0.0.1', HTTP_HOST='127.0.0.1')
print('appointment status', resp2.status_code)
soup2 = BeautifulSoup(resp2.content, 'html.parser')
select = soup2.find('select', attrs={'name': 'service'})
if not select:
    print('No service select found in appointment form')
    sys.exit(1)
selected = select.find('option', selected=True)
if selected:
    print('Preselected option:', selected.get_text().strip(), 'value=', selected.get('value'))
else:
    print('No option is preselected')
textarea = soup2.find('textarea', attrs={'name': 'message'})
if textarea:
    print('Message prefill:\n', textarea.text.strip())
else:
    print('No message textarea found')
