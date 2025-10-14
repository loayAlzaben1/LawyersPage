import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','lawyer_site.settings')
django.setup()
from core import tasks
from core.models import WebPushSubscription
subs = list(WebPushSubscription.objects.all().values_list('id', flat=True))
print('found subs', len(subs))
task = getattr(tasks, 'send_pushes_to_subscriptions')
print('has delay:', hasattr(task, 'delay'))
try:
    if hasattr(task, 'delay'):
        task.delay(subs, None, 'Dev enqueued title', 'Dev enqueued body', '/')
        print('task.delay called')
    else:
        task(subs, None, 'Dev enqueued title', 'Dev enqueued body', '/')
        print('task directly called')
except Exception as e:
    print('task call error', e)
