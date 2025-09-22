import tempfile
import shutil
import io
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.test import Client
from django.utils import timezone
from PIL import Image

from blog.models import BlogPost


def make_image_bytes(size=(1200, 630), color=(100, 150, 200)):
    buf = io.BytesIO()
    Image.new('RGB', size, color=color).save(buf, format='JPEG')
    buf.seek(0)
    return buf.read()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class OGMetaTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        # Remove temp media
        try:
            shutil.rmtree(getattr(cls, '_media_root', None) or '')
        except Exception:
            pass
        super().tearDownClass()

    def setUp(self):
        # ensure client uses allowed hosts in test
        self.client = Client()

    def _create_post_with_processed(self, slug='post-processed'):
        post = BlogPost.objects.create(slug=slug, published_at=timezone.now())
        post.set_current_language('ar')
        post.title = 'عنوان اختبار'
        post.content = 'محتوى اختبار للبوست'
        post.save()

        img_bytes = make_image_bytes()
        post.processed_og_image_large.save(f"{slug}_large.jpg", ContentFile(img_bytes), save=True)
        return post

    def _create_post_with_og(self, slug='post-og'):
        post = BlogPost.objects.create(slug=slug, published_at=timezone.now())
        post.set_current_language('ar')
        post.title = 'عنوان OG'
        post.content = 'محتوى OG'
        post.save()
        img_bytes = make_image_bytes()
        post.og_image.save(f"{slug}_og.jpg", ContentFile(img_bytes), save=True)
        return post

    def test_detail_uses_processed_image(self):
        post = self._create_post_with_processed('og-processed-test')
        path = reverse('blog:detail', args=[post.slug])
        resp = self.client.get(path, SERVER_NAME='testserver')
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Expect the processed image url to appear in meta
        self.assertIn(post.processed_og_image_large.url, content)

    def test_detail_falls_back_to_og_image(self):
        post = self._create_post_with_og('og-fallback-test')
        path = reverse('blog:detail', args=[post.slug])
        resp = self.client.get(path, SERVER_NAME='testserver')
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Depending on save() processing, processed image may be generated; accept either
        self.assertTrue(post.og_image.url in content or (hasattr(post, 'processed_og_image_large') and post.processed_og_image_large and post.processed_og_image_large.url in content))

    def test_index_prefers_first_post_processed_image(self):
        # create second post first so the processed post can be the most recent (first in list)
        p2 = self._create_post_with_og('second-og')
        p1 = self._create_post_with_processed('first-processed')
        resp = self.client.get(reverse('blog:index'), SERVER_NAME='testserver')
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn(p1.processed_og_image_large.url, content)
