from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from .validators import validate_file_size, validate_file_extension
from django.conf import settings


class LawyerProfile(TranslatableModel):
    translations = TranslatedFields(
        full_name=models.CharField(max_length=200),
        title=models.CharField(max_length=200, blank=True),
        bio=models.TextField(blank=True),
    )
    photo = models.ImageField(upload_to='lawyer_photos/', blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_address = models.CharField(max_length=255, blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    social_links = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('full_name', any_language=True) or 'Profile'


class Service(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        description=models.TextField(blank=True),
    )
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True)


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_datetime = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    attachment = models.FileField(upload_to='appointments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact: {self.name} - {self.created_at.date()}"


class SiteStats(models.Model):
    """Simple site-wide counters editable via admin.

    Use admin to set realistic numbers for cases_won and years_experience.
    """
    cases_won = models.PositiveIntegerField(default=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Stats'
        verbose_name_plural = 'Site Stats'

    def __str__(self):
        return f"Cases: {self.cases_won}"


class Case(models.Model):
    """Client case record for public listing. Editable in admin.

    Fields: title, summary, image (optional), published flag, created_at
    """
    title = models.CharField(max_length=250)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='case_images/', blank=True, null=True)
    # Rich fields
    case_type = models.CharField(max_length=120, blank=True, help_text='نوع القضية')
    outcome = models.CharField(max_length=120, blank=True, help_text='النتيجة')
    case_date = models.DateField(null=True, blank=True)
    client_initials = models.CharField(max_length=10, blank=True, help_text='مثال: أ.س')
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # relations
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL, related_name='cases')
    tag = models.ManyToManyField('Tag', blank=True, related_name='cases')
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def admin_thumbnail(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return f'<img src="{self.image.url}" style="height:60px;border-radius:6px;object-fit:cover;" />'
        except Exception:
            pass
        return ''
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = 'الصورة'



class CaseDocument(models.Model):
    case = models.ForeignKey(Case, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='case_docs/')
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or (self.file.name if self.file else 'وثيقة')


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'فئات'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = 'وسم'
        verbose_name_plural = 'وسوم'

    def __str__(self):
        return self.name


class CaseImage(models.Model):
    case = models.ForeignKey(Case, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='case_images/gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.caption or (self.image.name if self.image else 'صورة')


class Review(models.Model):
    """Customer review used on the homepage carousel.

    rating: 1-5 integer. Higher rating can be used to control slide duration.
    """
    name = models.CharField(max_length=140)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    avatar = models.ImageField(upload_to='review_avatars/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.pk} - {self.name} ({self.rating})"


class WebPushSubscription(models.Model):
    """Stores a browser push subscription for use with Web Push (VAPID).

    Fields follow the standard PushSubscription shape: endpoint and keys (p256dh, auth).
    """
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription {self.pk} - {self.endpoint[:60]}"


class PushNotificationLog(models.Model):
    """Simple log for push notification attempts.

    Records whether an attempt to notify a subscription succeeded or failed,
    plus optional HTTP response codes and error text for diagnosis.
    """
    subscription = models.ForeignKey(WebPushSubscription, null=True, blank=True, on_delete=models.SET_NULL)
    blogpost_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=(('sent', 'Sent'), ('failed', 'Failed')))
    response_code = models.IntegerField(null=True, blank=True)
    error_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PushLog {self.pk} - {self.status} - post:{self.blogpost_id} sub:{self.subscription_id}"


class Notification(models.Model):
    """Simple DB-backed notification for clients that poll the server.

    This is the fallback/simple alternative to Web Push when persistent
    background workers or push delivery are not available.
    """
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification {self.pk} - {self.title} - user:{self.user_id}"

