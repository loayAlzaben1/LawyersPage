from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

from ..models import BlogPost, Comment, NotificationLog


@override_settings(NOTIFY_EMAIL='lawyer@example.com', DEFAULT_FROM_EMAIL='site@example.com', NOTIFY_ON_APPROVE_DELETE=True, SITE_DOMAIN='example.com')
class CommentResendActionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin7', 'admin7@example.com', 'password')
        self.client.login(username='admin7', password='password')
        self.post = BlogPost.objects.create(slug='comment-resend-post')

    def test_resend_unapproved_comment(self):
        c = Comment.objects.create(post=self.post, name='Una', comment='Please review')
        mail.outbox = []
        url = reverse('admin:blog_comment_resend', args=[c.pk])
        response = self.client.post(url, {'resend_confirm': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        # A new NotificationLog should be created
        self.assertTrue(NotificationLog.objects.filter(related_comment=c, notify_type='created').exists())

    def test_resend_approved_comment(self):
        c = Comment.objects.create(post=self.post, name='Ap', comment='Approved comment', approved=True)
        mail.outbox = []
        url = reverse('admin:blog_comment_resend', args=[c.pk])
        response = self.client.post(url, {'resend_confirm': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(NotificationLog.objects.filter(related_comment=c, notify_type='approved').exists())

    def test_resend_get_not_allowed(self):
        c = Comment.objects.create(post=self.post, name='G', comment='GET test')
        url = reverse('admin:blog_comment_resend', args=[c.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_resend_post_without_confirm_redirects_and_no_send(self):
        c = Comment.objects.create(post=self.post, name='NoConfirm', comment='Should not send')
        mail.outbox = []
        url = reverse('admin:blog_comment_resend', args=[c.pk])
        # capture current counts (creation of the comment may create initial logs)
        before_mail_count = len(mail.outbox)
        before_log_count = NotificationLog.objects.filter(related_comment=c).count()

        # POST without resend_confirm should not trigger sending; follow redirect to capture messages
        response = self.client.post(url, {}, follow=True)
        # After following redirect, final status should be 200 (admin changelist)
        self.assertEqual(response.status_code, 200)
        # No additional emails sent
        self.assertEqual(len(mail.outbox), before_mail_count)
        # No new NotificationLog entries for this comment
        after_log_count = NotificationLog.objects.filter(related_comment=c).count()
        self.assertEqual(after_log_count, before_log_count)
        # Check for our error message in messages
        msgs = []
        if response.context and 'messages' in response.context:
            msgs = [m.message for m in response.context['messages']]
        self.assertTrue(any('لم يتم تأكيد إعادة الإرسال' in m for m in msgs))
