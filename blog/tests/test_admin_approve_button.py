from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import BlogPost, Comment


class AdminApproveButtonTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin2', 'admin2@example.com', 'password')
        self.client = Client()
        self.client.login(username='admin2', password='password')

        self.post = BlogPost.objects.create(slug='approve-post')
        self.comment = Comment.objects.create(post=self.post, name='Visitor', comment='Please approve', approved=False)

    def test_approve_view_approves_comment(self):
        url = reverse('admin:blog_comment_approve', args=[self.comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.approved)
        # Check for success message text
        self.assertContains(response, 'تم اعتماد التعليق')
