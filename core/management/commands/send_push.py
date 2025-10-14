from django.core.management.base import BaseCommand
from core.models import WebPushSubscription
from core import tasks as push_tasks

class Command(BaseCommand):
    help = 'Send a web push notification to all subscribers'

    def add_arguments(self, parser):
        parser.add_argument('title')
        parser.add_argument('body')

    def handle(self, *args, **options):
        title = options['title']
        body = options['body']
        # Enqueue a broadcast using the task if available. This keeps sending
        # asynchronous and reliable when Celery + Redis are configured.
        try:
            task = getattr(push_tasks, 'send_pushes_for_post')
            # Use blogpost_id=None for admin manual sends
            if hasattr(task, 'delay'):
                task.delay(None, title, body, '/')
            else:
                task(None, title, body, '/')
            self.stdout.write('Enqueued broadcast send via task.')
        except Exception as e:
            # Fallback: synchronous send
            subs = WebPushSubscription.objects.all()
            total = subs.count()
            self.stdout.write(f'Sending to {total} subscriptions (sync fallback)...')
            sent = 0
            from core.utils import send_webpush
            for s in subs:
                info = {'endpoint': s.endpoint, 'keys': {'p256dh': s.p256dh, 'auth': s.auth}}
                ok = send_webpush(info, title, body)
                if ok:
                    sent += 1
            self.stdout.write(f'Sent: {sent}, Failed/Skipped: {total - sent}')
