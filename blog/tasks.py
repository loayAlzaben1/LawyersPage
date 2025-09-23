from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import BlogPost


def _generate_processed_images(blogpost_pk):
    post = BlogPost.objects.filter(pk=blogpost_pk).first()
    if not post or not post.og_image:
        return

    try:
        post.og_image.open()
        img_bytes = post.og_image.read()
        img_orig = Image.open(BytesIO(img_bytes))
        img_orig = img_orig.convert('RGB')

        sizes = {
            'large': (1200, 630),
            'medium': (800, 420),
            'small': (400, 210),
        }

        saved_fields = []
        for key, (target_w, target_h) in sizes.items():
            img = img_orig.copy()
            src_w, src_h = img.size
            src_ratio = src_w / src_h if src_h else 1
            target_ratio = target_w / target_h

            if src_ratio > target_ratio:
                scale = target_h / src_h
            else:
                scale = target_w / src_w

            new_size = (int(src_w * scale) + 1, int(src_h * scale) + 1)
            img = img.resize(new_size, Image.LANCZOS)

            left = (img.width - target_w) // 2
            top = (img.height - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            img = img.crop((left, top, right, bottom))

            out_io = BytesIO()
            img.save(out_io, format='JPEG', quality=85)
            out_io.seek(0)

            slug_part = getattr(post, 'slug', None) or get_random_string(6)
            date_part = timezone.now().strftime('%Y%m%d')
            name = f"{slug_part}_{date_part}_{key}.jpg"

            field_name = f'processed_og_image_{key}'
            getattr(post, field_name).save(name, ContentFile(out_io.read()), save=False)
            saved_fields.append(field_name)

        post.save(update_fields=saved_fields)
    except Exception:
        # swallow exceptions to avoid breaking callers
        return


def process_og_images_for_post(pk):
    return _generate_processed_images(pk)


# Optional Celery task wrapper (importing Celery only if present at runtime)
try:
    # type: ignore - celery is optional; Pylance may not have it installed in the editor env
    from celery import shared_task  # type: ignore

    @shared_task
    def process_og_images_task(pk):
        return _generate_processed_images(pk)
except ImportError:
    # Celery not installed or configured; ignore
    pass
