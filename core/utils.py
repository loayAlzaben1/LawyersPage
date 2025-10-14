import json
from django.conf import settings

try:
    from pywebpush import webpush, WebPushException
except Exception:
    webpush = None
    WebPushException = Exception


def send_webpush(subscription_info, title, body, url='/', icon=None):
    """Send a web push notification using pywebpush. Returns True on success.

    If pywebpush is not installed, this function returns False (no-op).
    """
    if webpush is None:
        return False

    vapid_private = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims = {
        'sub': getattr(settings, 'VAPID_CLAIMS_SUBJECT', 'mailto:admin@example.com')
    }
    payload = {
        'title': title,
        'body': body,
        'icon': icon or getattr(settings, 'DEFAULT_NOTIFICATION_ICON', '/static/img/android-chrome-192x192.png'),
        'url': url,
    }
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=vapid_private,
            vapid_claims=vapid_claims
        )
        return True
    except WebPushException:
        # Might be an invalid/expired subscription
        return False


def send_webpush_with_result(subscription_info, title, body, url='/', icon=None):
    """Send and return a dict with outcome details: {'ok': bool, 'code': int|None, 'error': str|None}

    This exposes HTTP status codes when available so callers can prune subscriptions on 404/410.
    If pywebpush isn't installed, returns {'ok': False, 'code': None, 'error': 'pywebpush missing'}
    """
    if webpush is None:
        return {'ok': False, 'code': None, 'error': 'pywebpush missing'}

    vapid_private = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims = {
        'sub': getattr(settings, 'VAPID_CLAIMS_SUBJECT', 'mailto:admin@example.com')
    }
    payload = {
        'title': title,
        'body': body,
        'icon': icon or getattr(settings, 'DEFAULT_NOTIFICATION_ICON', '/static/img/android-chrome-192x192.png'),
        'url': url,
    }
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=vapid_private,
            vapid_claims=vapid_claims
        )
        # pywebpush doesn't return an HTTP code on success; consider success without code
        return {'ok': True, 'code': None, 'error': None}
    except WebPushException as exc:
        # pywebpush's WebPushException may expose response details. Try to extract status codes
        code = None
        error_text = None
        try:
            error_text = str(exc)
        except Exception:
            error_text = 'webpush exception'

        try:
            # pywebpush often attaches a `response` attribute similar to requests.Response
            resp = getattr(exc, 'response', None)
            if resp is not None:
                # requests.Response uses status_code and text; some wrappers use .status
                code = getattr(resp, 'status_code', None) or getattr(resp, 'status', None) or getattr(resp, 'code', None)
                # attempt to get response body for debugging
                try:
                    body = getattr(resp, 'text', None)
                    if not body:
                        # some objects have content or body
                        body = getattr(resp, 'content', None)
                        if isinstance(body, (bytes, bytearray)):
                            try:
                                body = body.decode('utf-8', errors='replace')
                            except Exception:
                                body = repr(body)
                    if body:
                        # include a short snippet
                        error_text = (error_text or '') + '\n' + (body[:1000] if isinstance(body, str) else str(body))
                except Exception:
                    pass
        except Exception:
            # best-effort extraction only
            pass

        return {'ok': False, 'code': code, 'error': error_text}


def send_webpush_to_subscription_obj(sub_obj, title, body, url='/', icon=None):
    """Convenience wrapper: accepts a WebPushSubscription instance and sends a push.

    Returns the same dict as send_webpush_with_result.
    """
    if sub_obj is None:
        return {'ok': False, 'code': None, 'error': 'no subscription'}
    info = {'endpoint': sub_obj.endpoint, 'keys': {'p256dh': sub_obj.p256dh, 'auth': sub_obj.auth}}
    return send_webpush_with_result(info, title=title, body=body, url=url, icon=icon)
