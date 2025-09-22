from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from .models import Comment, NotificationLog


@receiver(post_save, sender=Comment)
def notify_on_new_comment(sender, instance, created, **kwargs):
    # Only notify for newly created, non-approved comments
    if not created:
        return
    if instance.approved:
        return

    recipient = getattr(settings, 'NOTIFY_EMAIL', None)
    if not recipient:
        return

    # Build admin change URL for the comment (absolute)
    # Attempt to build a sensible domain: prefer settings.SITE_DOMAIN, then ALLOWED_HOSTS, else example.com
    domain = getattr(settings, 'SITE_DOMAIN', None)
    if not domain:
        allowed = getattr(settings, 'ALLOWED_HOSTS', [])
        domain = allowed[0] if allowed else 'example.com'

    admin_url = f'https://{domain}' + reverse('admin:blog_comment_change', args=[instance.pk])

    subject = 'تعليق جديد قيد المراجعة'
    message = f"وصول تعليق جديد على المقال: {instance.post}\n\nمن: {instance.name or 'زائر'}\n\n{instance.comment}\n\nراجع التعليق هنا: {admin_url}"

    try:
        send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [recipient])
        sent = True
    except Exception:
        sent = False

    # Record audit log
    NotificationLog.objects.create(
        notify_type='created',
        comment_text=instance.comment,
        commenter_name=instance.name or '',
        sent=sent,
        related_comment=instance,
    )
