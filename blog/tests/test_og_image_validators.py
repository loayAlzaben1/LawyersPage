from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from core.validators import validate_og_image
from PIL import Image
import io


def make_image_bytes(mode='RGB', size=(1200, 630), fmt='JPEG', color=(255, 0, 0)):
    buf = io.BytesIO()
    img = Image.new(mode, size, color)
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


class OGImageValidatorTests(SimpleTestCase):
    def test_accepts_valid_image(self):
        data = make_image_bytes(size=(1200, 630), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')
        # Should not raise
        validate_og_image(f)

    def test_rejects_too_small_image(self):
        data = make_image_bytes(size=(800, 600), fmt='JPEG')
        f = SimpleUploadedFile('small.jpg', data, content_type='image/jpeg')
        with self.assertRaises(Exception):
            validate_og_image(f)

    def test_rejects_bad_aspect_ratio(self):
        data = make_image_bytes(size=(1200, 800), fmt='JPEG')
        f = SimpleUploadedFile('wide.jpg', data, content_type='image/jpeg')
        with self.assertRaises(Exception):
            validate_og_image(f)

    def test_rejects_large_file(self):
        # Simulate large file by creating a big byte sequence (but valid image header)
        data = make_image_bytes(size=(2000, 2000), fmt='JPEG')
        # Pad to exceed 5MB
        if len(data) < 6 * 1024 * 1024:
            data = data + b'0' * (6 * 1024 * 1024 - len(data))
        f = SimpleUploadedFile('big.jpg', data, content_type='image/jpeg')
        with self.assertRaises(Exception):
            validate_og_image(f)


from django.test import TestCase
from blog.models import BlogPost


class OGImageProcessingTests(TestCase):
    def test_processed_image_generated_on_save(self):
        # Create an in-memory image that passes validation
        data = make_image_bytes(size=(1600, 900), fmt='JPEG')
        f = SimpleUploadedFile('og.jpg', data, content_type='image/jpeg')

        post = BlogPost.objects.create(slug='test-post')
        # assign and save
        post.og_image.save('og.jpg', f, save=True)

        post.refresh_from_db()
        self.assertTrue(post.processed_og_image)
        self.assertTrue(getattr(post.processed_og_image, 'name', ''))
