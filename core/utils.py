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
