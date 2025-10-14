from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from unittest import mock
from ..admin import CustomUserAdmin
from ..models import WebPushSubscription

User = get_user_model()


class DummyRequest:
    def __init__(self, user):
        self.user = user


class WebPushAdminActionTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.user = User.objects.create_user(username='tester', password='pass')
        # create a subscription for this user
        self.sub = WebPushSubscription.objects.create(endpoint='https://example.com/1', p256dh='p', auth='a', user=self.user)
        self.admin = CustomUserAdmin(User, self.site)
        self.request = RequestFactory().get('/')
        self.request.user = self.user

    def test_admin_action_uses_task_delay_if_available(self):
        # mock tasks.send_pushes_to_subscriptions with a .delay attribute
        fake_task = mock.MagicMock()
        fake_task.delay = mock.MagicMock()
        with mock.patch('core.admin.push_tasks', new=mock.MagicMock(send_pushes_to_subscriptions=fake_task)):
            # run the action
            qs = User.objects.filter(pk=self.user.pk)
            # This should call .delay on the fake task
            self.admin.send_notification_to_user_subscriptions(self.request, qs)
            self.assertTrue(fake_task.delay.called)

    def test_admin_action_fallbacks_to_sync_when_task_missing(self):
        # simulate tasks missing or no delay
        # patch the tasks import path to raise
        with mock.patch('core.admin.push_tasks', new=None):
            qs = User.objects.filter(pk=self.user.pk)
            # Should not raise
            self.admin.send_notification_to_user_subscriptions(self.request, qs)
            # Verify the subscription still exists and nothing crashed
            self.assertTrue(WebPushSubscription.objects.filter(user=self.user).exists())
