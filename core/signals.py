from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from blog.models import BlogPost
from .models import WebPushSubscription
from . import tasks as push_tasks
from .models import Appointment, Case
from .models import Notification
from django.db.models.signals import pre_save


# Keep existing BlogPost publish handler above ...


@receiver(post_save, sender=BlogPost)
def blogpost_post_save(sender, instance, created, **kwargs):
    """When a BlogPost becomes published (published_at set), send a notification to all subscriptions.

    Logic:
    - If the instance was just saved with a non-null published_at and previously it was null (newly published), or
      if created=True and published_at is set, treat as publish event.
    - Iterate subscriptions, call send_webpush for each. If send_webpush returns False, delete the subscription.
    - This handler is intentionally simple; for high-volume sites consider offloading to Celery/queue.
    """
    try:
        was_published_before = False
        if instance.pk and not created:
            # Attempt to fetch previous state
            try:
                prev = sender.objects.get(pk=instance.pk)
                # If previous published_at was set and is same as current, don't treat as new publish
                was_published_before = bool(prev.published_at)
            except sender.DoesNotExist:
                was_published_before = False
        # Determine if this save represents a publish event
        now_published = bool(instance.published_at)
        is_new_publish = (now_published and (created or not was_published_before))

        if not is_new_publish:
            return

        title = instance.safe_translation_getter('title', any_language=True) or 'مقال جديد'
        # Short body: use beginning of content or a fixed message
        content = instance.safe_translation_getter('content', any_language=True) or ''
        body = (content[:120] + '...') if len(content) > 120 else content or 'تم نشر مقال جديد'
        url = instance.get_absolute_url() or '/'

        # Enqueue the background task to notify subscribers. If Celery is not
        # available, `send_pushes_for_post` is a synchronous fallback function.
        try:
            task = getattr(push_tasks, 'send_pushes_for_post')
            # If Celery task, use .delay(); else call directly
            if hasattr(task, 'delay'):
                task.delay(instance.pk, title, body, url)
            else:
                # synchronous fallback
                task(instance.pk, title, body, url)
        except Exception:
            # Swallow any errors to keep save() non-failing
            pass
        # Do not create DB Notification with user=None (polling only returns user-specific notifications).
        # Broadcasts should use push (web push) rather than DB notifications for anonymous/public messages.
    except Exception:
        # Never let errors during notification sending break the save flow
        pass


@receiver(post_save, sender=Appointment)
def appointment_post_save(sender, instance, created, **kwargs):
    """Notify the user when their appointment status changes to 'confirmed'.

    If the Appointment has an email and there are subscriptions linked to that user
    (or none), this will try to send to subscriptions matching the appointment's user
    if available; otherwise it will attempt to send to any subscriptions with the
    same email attached via the user profile (if present).
    """
    try:
        # detect transition to confirmed or cancelled (rejected)
        was_status_before = None
        if instance.pk and not created:
            try:
                prev = sender.objects.get(pk=instance.pk)
                was_status_before = prev.status
            except Exception:
                was_status_before = None

        is_now_confirmed = (instance.status == 'confirmed') and (was_status_before != 'confirmed')
        is_now_cancelled = (instance.status == 'cancelled') and (was_status_before != 'cancelled')

        if not (is_now_confirmed or is_now_cancelled):
            return

        if is_now_confirmed:
            title = 'حجز تم تأكيده'
            body = f'تم تأكيد حجزك باسم {instance.name}. سنقوم بالتواصل معك.'
        else:
            title = 'حجز تم إلغاؤه'
            body = f'نأسف لإبلاغك أن الحجز باسم {instance.name} تم إلغاؤه. تواصل معنا لتحديد موعد آخر.'

        url = '/'  # could be appointment detail in a real app

        # prefer user-linked subscriptions
        subs = WebPushSubscription.objects.none()
        if instance.email:
            # try to find a user with this email and their subscriptions
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(email__iexact=instance.email).first()
                if user:
                    subs = WebPushSubscription.objects.filter(user=user)
            except Exception:
                subs = WebPushSubscription.objects.none()

        # fallback: all subscriptions (or consider matching by phone/email field mapping)
        if not subs.exists():
            subs = WebPushSubscription.objects.all()

        # send via task if available
        try:
            task = getattr(push_tasks, 'send_pushes_to_subscriptions')
            ids = list(subs.values_list('id', flat=True))
            if hasattr(task, 'delay'):
                task.delay(ids, instance.pk, title, body, url)
            else:
                task(ids, instance.pk, title, body, url)
        except Exception:
            pass
        # Create a DB notification: prefer attaching to a resolved user, otherwise create a
        # Notification with user=None so polling clients can still surface the event (admin/cleanup may later reassign).
        try:
            target_user = None
            if instance.email:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                target_user = User.objects.filter(email__iexact=instance.email).first()
            Notification.objects.create(user=target_user, title=title, message=body)
        except Exception:
            pass
    except Exception:
        pass


@receiver(post_save, sender=Case)
def case_post_save(sender, instance, created, **kwargs):
    """When a case becomes published (published=True) notify all subscribers.

    Uses the same background task as blog posts.
    """
    try:
        was_published_before = False
        if instance.pk and not created:
            try:
                prev = sender.objects.get(pk=instance.pk)
                was_published_before = bool(prev.published)
            except Exception:
                was_published_before = False
        now_published = bool(instance.published)
        is_new_publish = now_published and (created or not was_published_before)
        if not is_new_publish:
            return

        title = f'قضية جديدة: {instance.title}'
        body = (instance.summary[:120] + '...') if instance.summary else 'تم نشر حالة جديدة'
        url = '/'  # could be a case detail URL
        try:
            task = getattr(push_tasks, 'send_pushes_for_post')
            if hasattr(task, 'delay'):
                task.delay(instance.pk, title, body, url)
            else:
                task(instance.pk, title, body, url)
        except Exception:
            pass

        # Also create per-user DB Notifications for staff/non-staff consumers.
        # If the case is a site-level published item, admins may want users to see
        # a record in the in-app notification center (polling clients).
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # Create notifications for all active non-staff users (customers)
            recipients = User.objects.filter(is_active=True, is_staff=False)
            notes = [Notification(user=u, title=title, message=body) for u in recipients]
            Notification.objects.bulk_create(notes)
        except Exception:
            # Don't let notification creation break the save flow
            pass
    except Exception:
        pass
