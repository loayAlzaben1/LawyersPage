from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import BlogPost
from .test_og_image_validators import make_image_bytes


class TemplateMetaTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_detail_uses_processed_image_in_meta(self):
        data = make_image_bytes(size=(1600, 900), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')

        post = BlogPost.objects.create(slug='meta-test')
        # Assign original and trigger processing
        post.og_image.save('og.jpg', f, save=True)
        post.refresh_from_db()

        url = reverse('blog:detail', args=[post.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Expect processed large image URL in meta
        self.assertIn('property="og:image"', content)
        self.assertIn(post.processed_og_image_large.url, content)

    def test_detail_includes_canonical_and_jsonld(self):
        data = make_image_bytes(size=(1600, 900), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')

        post = BlogPost.objects.create(slug='meta-test-2')
        post.og_image.save('og.jpg', f, save=True)
        post.refresh_from_db()

        url = reverse('blog:detail', args=[post.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn('<link rel="canonical"', content)
        self.assertIn('application/ld+json', content)

    def test_comments_form_rendered(self):
        data = make_image_bytes(size=(1600, 900), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')

        post = BlogPost.objects.create(slug='meta-test-3')
        post.og_image.save('og.jpg', f, save=True)
        post.refresh_from_db()

        url = reverse('blog:detail', args=[post.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Comment form includes a textarea or name="comment"
        self.assertTrue('name="comment"' in content or '<textarea' in content)

    def test_can_post_comment_and_stored_unapproved(self):
        data = make_image_bytes(size=(1600, 900), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')

        post = BlogPost.objects.create(slug='meta-test-4')
        post.og_image.save('og.jpg', f, save=True)
        post.refresh_from_db()

        url = reverse('blog:detail', args=[post.slug])
        resp = self.client.post(url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'comment': 'This is a test comment.'
        })
        # After posting, should redirect
        self.assertEqual(resp.status_code, 302)
        # Comment should exist in DB and be unapproved
        from blog.models import Comment
        c = Comment.objects.filter(post=post, comment__icontains='test comment').first()
        self.assertIsNotNone(c)
        self.assertFalse(c.approved)
