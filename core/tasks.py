from django.conf import settings
from django.utils import timezone

from .models import WebPushSubscription, PushNotificationLog
from .utils import send_webpush_with_result


def _send_pushes_for_post(blogpost_id, title, body, url='/', icon=None):
    """Core logic to iterate subscriptions, send notifications, prune invalid ones, and log results."""
    subs = WebPushSubscription.objects.all()
    results = {'sent': 0, 'failed': 0, 'pruned': 0}
    for s in subs:
        info = {
            'endpoint': s.endpoint,
            'keys': {'p256dh': s.p256dh, 'auth': s.auth}
        }
        res = send_webpush_with_result(info, title=title, body=body, url=url, icon=icon)
        if res.get('ok'):
            results['sent'] += 1
            PushNotificationLog.objects.create(subscription=s, blogpost_id=blogpost_id, status='sent')
        else:
            results['failed'] += 1
            code = res.get('code')
            PushNotificationLog.objects.create(subscription=s, blogpost_id=blogpost_id, status='failed', response_code=code, error_text=res.get('error') or '')
            # If the response code indicates the subscription is gone/invalid, delete it
            try:
                if code in (404, 410):
                    s.delete()
                    results['pruned'] += 1
            except Exception:
                # Ignore deletion errors
                pass
    return results


def _send_pushes_to_subscriptions(sub_qs, context_id=None, title=None, body=None, url='/', icon=None):
    """Send notifications to a queryset or iterable of WebPushSubscription objects.

    context_id: optional integer referring to the triggering object (appointment id, case id, etc.)
    """
    results = {'sent': 0, 'failed': 0, 'pruned': 0}
    for s in sub_qs:
        try:
            res = send_webpush_with_result({'endpoint': s.endpoint, 'keys': {'p256dh': s.p256dh, 'auth': s.auth}}, title=title, body=body, url=url, icon=icon)
            if res.get('ok'):
                results['sent'] += 1
                PushNotificationLog.objects.create(subscription=s, blogpost_id=context_id, status='sent')
            else:
                results['failed'] += 1
                code = res.get('code')
                PushNotificationLog.objects.create(subscription=s, blogpost_id=context_id, status='failed', response_code=code, error_text=res.get('error') or '')
                if code in (404, 410):
                    try:
                        s.delete()
                        results['pruned'] += 1
                    except Exception:
                        pass
        except Exception:
            results['failed'] += 1
    return results


# Task wrapper for targeted sends
try:
    from celery import shared_task

    @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
    def send_pushes_to_subscriptions(self, subscription_ids, context_id, title, body, url='/', icon=None):
        from .models import WebPushSubscription
        subs = WebPushSubscription.objects.filter(id__in=subscription_ids)
        return _send_pushes_to_subscriptions(subs, context_id=context_id, title=title, body=body, url=url, icon=icon)

except Exception:
    def send_pushes_to_subscriptions(subscription_ids, context_id, title, body, url='/', icon=None):
        from .models import WebPushSubscription
        subs = WebPushSubscription.objects.filter(id__in=subscription_ids)
        return _send_pushes_to_subscriptions(subs, context_id=context_id, title=title, body=body, url=url, icon=icon)


# Try to register a Celery task if Celery is available. If not, expose a sync function.
try:
    from celery import shared_task

    @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
    def send_pushes_for_post(self, blogpost_id, title, body, url='/', icon=None):
        """Celery task wrapper that retries on exceptions and calls the core sending function."""
        return _send_pushes_for_post(blogpost_id, title, body, url=url, icon=icon)

except Exception:
    # No Celery available; provide a synchronous fallback
    def send_pushes_for_post(blogpost_id, title, body, url='/', icon=None):
        return _send_pushes_for_post(blogpost_id, title, body, url=url, icon=icon)
