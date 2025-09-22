from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import BlogPost, Comment


class AdminDeleteButtonTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin3', 'admin3@example.com', 'password')
        self.client = Client()
        self.client.login(username='admin3', password='password')

        self.post = BlogPost.objects.create(slug='delete-post')
        self.comment = Comment.objects.create(post=self.post, name='Visitor', comment='Please delete me', approved=False)

    def test_delete_view_deletes_comment(self):
        url = reverse('admin:blog_comment_delete', args=[self.comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertContains(response, 'تم حذف التعليق بنجاح')
