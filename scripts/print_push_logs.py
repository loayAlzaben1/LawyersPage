import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','lawyer_site.settings')
import django
django.setup()
from core.models import PushNotificationLog
logs = PushNotificationLog.objects.order_by('-created_at')[:20]
print('Found', logs.count(), 'log entries')
for l in logs:
    print(l.created_at.isoformat(), l.status, l.response_code, (l.error_text or '')[:300])
