"""Ad-hoc inspect script: prints WebPushSubscription, Notification, and PushNotificationLog summaries.
Run with: .\.venv\Scripts\Activate.ps1; python scripts\inspect_notifications.py
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import WebPushSubscription, Notification, PushNotificationLog

User = get_user_model()

print('Users:')
for u in User.objects.all():
    subs = WebPushSubscription.objects.filter(user=u)
    notes = Notification.objects.filter(user=u)
    print(f'- {u.pk} {getattr(u, "username", str(u))} subscriptions={subs.count()} notifications={notes.count()}')

print('\nRecent subscriptions:')
for s in WebPushSubscription.objects.all().order_by('-id')[:20]:
    print(s.pk, s.user_id, s.endpoint[:80])

print('\nRecent notifications:')
for n in Notification.objects.all().order_by('-created_at')[:20]:
    print(n.id, n.user_id, n.is_read, n.created_at, (n.title or '')[:40], (n.message or '')[:80])

print('\nRecent push logs:')
for l in PushNotificationLog.objects.all().order_by('-created_at')[:50]:
    print(l.id, l.subscription_id, l.status, l.response_code, (l.error_text or '')[:120], l.created_at)
