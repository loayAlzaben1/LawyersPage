from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

from ..models import BlogPost, Comment, NotificationLog


@override_settings(NOTIFY_EMAIL='lawyer@example.com', DEFAULT_FROM_EMAIL='site@example.com', NOTIFY_ON_APPROVE_DELETE=True, SITE_DOMAIN='example.com')
class NotificationLogTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin5', 'admin5@example.com', 'password')
        self.client.login(username='admin5', password='password')
        self.post = BlogPost.objects.create(slug='log-post')

    def test_log_created_on_comment_creation(self):
        c = Comment.objects.create(post=self.post, name='Alice', comment='Hello')
        # Signal should create a NotificationLog for 'created'
        logs = NotificationLog.objects.filter(notify_type='created', related_comment=c)
        self.assertTrue(logs.exists())

    def test_log_created_on_approve(self):
        c = Comment.objects.create(post=self.post, name='Bob', comment='Please approve')
        mail.outbox = []
        url = reverse('admin:blog_comment_approve', args=[c.pk])
        self.client.get(url)
        logs = NotificationLog.objects.filter(notify_type='approved', related_comment=c)
        self.assertTrue(logs.exists())

    def test_log_created_on_delete(self):
        c = Comment.objects.create(post=self.post, name='Eve', comment='Delete me')
        mail.outbox = []
        url = reverse('admin:blog_comment_delete', args=[c.pk])
        self.client.get(url)
        logs = NotificationLog.objects.filter(notify_type='deleted')
        # there should be a 'deleted' entry (related_comment is None because we set it that way)
        self.assertTrue(logs.exists())
