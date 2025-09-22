from django.test import TestCase
from django.urls import reverse
from ..models import BlogPost, Comment


class HoneypotCommentTests(TestCase):
    def setUp(self):
        self.post = BlogPost.objects.create(slug='hp-post')

    def test_normal_submission_creates_comment(self):
        url = reverse('blog:detail', args=[self.post.slug])
        data = {
            'name': 'User',
            'email': 'u@example.com',
            'comment': 'A thoughtful comment',
            'hp_field': '',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)
        c = Comment.objects.get(post=self.post)
        self.assertFalse(c.approved)

    def test_honeypot_filled_rejected(self):
        url = reverse('blog:detail', args=[self.post.slug])
        data = {
            'name': 'Spammer',
            'email': 's@spam.example',
            'comment': 'Buy cheap meds',
            'hp_field': 'I am a bot',
        }
        response = self.client.post(url, data)
        # Expect 200 with form errors (no redirect)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spam detected')
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)
