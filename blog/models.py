from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import io
from PIL import Image

from core.validators import validate_og_image
from parler.models import TranslatableModel, TranslatedFields
from django.utils import timezone


class BlogPost(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        content=models.TextField(),
    )
    slug = models.SlugField(unique=True)
    published_at = models.DateTimeField(null=True, blank=True)
    featured_image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    og_image = models.ImageField(
        upload_to='og_images/', null=True, blank=True,
        validators=[validate_og_image],
        help_text='يفضل 1200x630px، صيغ JPG أو PNG، وحجم لا يتجاوز 5 ميغابايت'
    )

    # Processed copies used for meta tags (generated automatically on save)
    processed_og_image_large = models.ImageField(
        upload_to='og_images/processed/large/', null=True, blank=True,
        editable=False,
        help_text='صورة معالجة بالحجم 1200x630px (تُولد تلقائيًا)'
    )
    processed_og_image_medium = models.ImageField(
        upload_to='og_images/processed/medium/', null=True, blank=True,
        editable=False,
        help_text='صورة معالجة بالحجم 800x420px (تُولد تلقائيًا)'
    )
    processed_og_image_small = models.ImageField(
        upload_to='og_images/processed/small/', null=True, blank=True,
        editable=False,
        help_text='صورة معالجة بالحجم 400x210px (تُولد تلقائيًا)'
    )

    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        if title:
            return title
        # Fallback to slug or a generic representation to ensure a string is returned
        return getattr(self, 'slug', '') or f'Post {self.pk or ""}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # First save to ensure og_image file is available in storage
        super().save(*args, **kwargs)

        try:
            if self.og_image:
                # Open original image bytes
                self.og_image.open()
                img_bytes = self.og_image.read()
                img_orig = Image.open(io.BytesIO(img_bytes))
                img_orig = img_orig.convert('RGB')

                sizes = {
                    'large': (1200, 630),
                    'medium': (800, 420),
                    'small': (400, 210),
                }

                saved_fields = []

                for key, (target_w, target_h) in sizes.items():
                    img = img_orig.copy()

                    # Resize while keeping aspect, then center-crop to target
                    src_w, src_h = img.size
                    src_ratio = src_w / src_h if src_h else 1
                    target_ratio = target_w / target_h

                    if src_ratio > target_ratio:
                        # source is wider: fit height then crop width
                        scale = target_h / src_h
                    else:
                        # source is taller or equal: fit width then crop height
                        scale = target_w / src_w

                    new_size = (int(src_w * scale) + 1, int(src_h * scale) + 1)
                    img = img.resize(new_size, Image.LANCZOS)

                    # Center crop
                    left = (img.width - target_w) // 2
                    top = (img.height - target_h) // 2
                    right = left + target_w
                    bottom = top + target_h
                    img = img.crop((left, top, right, bottom))

                    out_io = io.BytesIO()
                    img.save(out_io, format='JPEG', quality=85)
                    out_io.seek(0)

                    # Create a filename including slug and date for readability
                    # Use slugify with allow_unicode so Arabic slugs remain readable
                    raw_slug = getattr(self, 'slug', None) or get_random_string(6)
                    slug_part = slugify(raw_slug, allow_unicode=True)
                    # Include PK to ensure uniqueness even if the same slug is reused
                    pk_part = getattr(self, 'pk', None) or get_random_string(6)
                    date_part = timezone.now().strftime('%Y%m%d')
                    name = f"{slug_part}-{pk_part}_{date_part}_{key}.jpg"

                    field_name = f'processed_og_image_{key}'
                    # Save to the corresponding processed field without recursion
                    getattr(self, field_name).save(name, ContentFile(out_io.read()), save=False)
                    saved_fields.append(field_name)

                # Persist only the processed image fields that were updated
                super().save(update_fields=saved_fields)
        except Exception:
            # Don't prevent saving the model if processing fails; leave processed fields empty
            pass

        # If configured, delegate processing to Celery (post-save). We won't block save.
        try:
            if getattr(settings, 'USE_CELERY_FOR_IMAGE_PROCESSING', False):
                # Import task lazily to avoid hard dependency
                from . import tasks as blog_tasks
                # If a Celery task wrapper exists, call it asynchronously, else call sync helper
                if hasattr(blog_tasks, 'process_og_images_task'):
                    try:
                        blog_tasks.process_og_images_task.delay(self.pk)
                    except Exception:
                        # If Celery not running or delay fails, fall back to sync processing
                        blog_tasks.process_og_images_for_post(self.pk)
                else:
                    blog_tasks.process_og_images_for_post(self.pk)
        except Exception:
            # Never raise during save; processing failures should not block the CMS
            pass


class Comment(models.Model):
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.name or 'Anonymous'} on {self.post}"
    

class NotificationLog(models.Model):
    NOTIFY_TYPE_CHOICES = [
        ('created', 'Created'),
        ('approved', 'Approved'),
        ('deleted', 'Deleted'),
    ]

    notify_type = models.CharField(max_length=20, choices=NOTIFY_TYPE_CHOICES)
    comment_text = models.TextField(blank=True)
    commenter_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    related_comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notify_type_display()} - {self.commenter_name} - {self.created_at.date()}"


class LawyerCard(models.Model):
    """A small editable card for the homepage representing a lawyer or team member.

    Editable from the admin: name, bio (short), optional image, ordering and active flag.
    The image is intended to take approximately half of the card width in the frontend.
    """
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='lawyer_cards/', null=True, blank=True,
                              validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    order = models.IntegerField(default=0, help_text='Lower numbers appear first')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name or f'Lawyer {self.pk or ""}'

    def admin_thumbnail(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return f'<img src="{self.image.url}" style="height:60px;border-radius:6px;object-fit:cover;" />'
        except Exception:
            pass
        return ''
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = 'الصورة'

