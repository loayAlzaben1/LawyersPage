from django.test import TestCase, override_settings
from django.core import mail
from django.urls import reverse

from ..models import BlogPost, Comment


@override_settings(NOTIFY_EMAIL='lawyer@example.com', DEFAULT_FROM_EMAIL='site@example.com', SITE_DOMAIN='example.com')
class CommentNotificationTests(TestCase):
    def setUp(self):
        self.post = BlogPost.objects.create(slug='notify-post')

    def test_notification_sent_on_new_unapproved_comment(self):
        # No emails initially
        self.assertEqual(len(mail.outbox), 0)

        # Create a new comment (unapproved by default)
        Comment.objects.create(post=self.post, name='Visitor', comment='Please notify')

        # One email should be sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('تعليق جديد قيد المراجعة', email.subject)
        self.assertIn('Please notify', email.body)
        self.assertIn('https://example.com', email.body)