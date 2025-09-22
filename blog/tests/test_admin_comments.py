from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import BlogPost, Comment


class AdminCommentApprovalTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client = Client()
        self.client.login(username='admin', password='password')

        # Create a blog post and a comment
        self.post = BlogPost.objects.create(slug='test-post')
        self.comment = Comment.objects.create(post=self.post, name='Visitor', email='v@example.com', comment='Nice post', approved=False)

    def test_admin_can_approve_comments_action(self):
        changelist_url = reverse('admin:blog_comment_changelist')

        # Ensure the comment starts unapproved
        self.assertFalse(Comment.objects.get(pk=self.comment.pk).approved)

        # Post the action 'approve_comments' with the selected comment
        response = self.client.post(changelist_url, {
            'action': 'approve_comments',
            '_selected_action': [str(self.comment.pk)],
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        # Reload and assert approved
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.approved)
