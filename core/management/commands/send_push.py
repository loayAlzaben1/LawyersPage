from django.core.management.base import BaseCommand
from core.models import WebPushSubscription
from core.utils import send_webpush

class Command(BaseCommand):
    help = 'Send a web push notification to all subscribers'

    def add_arguments(self, parser):
        parser.add_argument('title')
        parser.add_argument('body')

    def handle(self, *args, **options):
        title = options['title']
        body = options['body']
        subs = WebPushSubscription.objects.all()
        total = subs.count()
        self.stdout.write(f'Sending to {total} subscriptions...')
        sent = 0
        for s in subs:
            info = {
                'endpoint': s.endpoint,
                'keys': {
                    'p256dh': s.p256dh,
                    'auth': s.auth,
                }
            }
            ok = send_webpush(info, title, body)
            if ok:
                sent += 1
        self.stdout.write(f'Sent: {sent}, Failed/Skipped: {total - sent}')
