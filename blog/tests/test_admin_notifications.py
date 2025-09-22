from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from ..models import BlogPost, Comment


@override_settings(NOTIFY_EMAIL='lawyer@example.com', DEFAULT_FROM_EMAIL='site@example.com', NOTIFY_ON_APPROVE_DELETE=True)
class AdminNotificationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin4', 'admin4@example.com', 'password')
        self.client.login(username='admin4', password='password')
        self.post = BlogPost.objects.create(slug='notify-admin-post')

    def test_email_sent_on_approve(self):
        comment = Comment.objects.create(post=self.post, name='Visitor', comment='Approve me')
        # Clear any email sent by creation signal; we're testing the approve notification
        mail.outbox = []
        url = reverse('admin:blog_comment_approve', args=[comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that an email was sent with ✅ in subject
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('✅', mail.outbox[0].subject)
        self.assertIn('Approve me', mail.outbox[0].body)

    def test_email_sent_on_delete(self):
        comment = Comment.objects.create(post=self.post, name='Visitor', comment='Delete me now')
        # Clear any email sent by creation signal
        mail.outbox = []
        url = reverse('admin:blog_comment_delete', args=[comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('🗑️', mail.outbox[0].subject)
        self.assertIn('Delete me now', mail.outbox[0].body)
