from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

from ..models import BlogPost, Comment, NotificationLog


@override_settings(NOTIFY_EMAIL='lawyer@example.com', DEFAULT_FROM_EMAIL='site@example.com', NOTIFY_ON_APPROVE_DELETE=True, SITE_DOMAIN='example.com')
class NotificationResendTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin6', 'admin6@example.com', 'password')
        self.client.login(username='admin6', password='password')
        self.post = BlogPost.objects.create(slug='resend-post')

    def test_per_row_resend(self):
        c = Comment.objects.create(post=self.post, name='Sam', comment='Notify me')
        # There should be a created log
        orig_log = NotificationLog.objects.filter(notify_type='created', related_comment=c).first()
        self.assertIsNotNone(orig_log)
        mail.outbox = []
        url = reverse('admin:blog_notificationlog_resend', args=[orig_log.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        # A new log entry should be created for the resend
        self.assertEqual(NotificationLog.objects.filter(notify_type='created').count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_bulk_resend(self):
        c1 = Comment.objects.create(post=self.post, name='A', comment='One')
        c2 = Comment.objects.create(post=self.post, name='B', comment='Two')
        logs = NotificationLog.objects.filter(notify_type='created')
        self.assertEqual(logs.count(), 2)
        mail.outbox = []
        changelist_url = reverse('admin:blog_notificationlog_changelist')
        data = {
            'action': 'resend_notifications',
            '_selected_action': [str(l.pk) for l in logs],
        }
        response = self.client.post(changelist_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Two resends => two new logs and two emails
        self.assertEqual(NotificationLog.objects.filter(notify_type='created').count(), 4)
        self.assertEqual(len(mail.outbox), 2)
