from django.core.checks import Error, register
from django.conf import settings

VAPID_SETTING_NAMES = ('VAPID_PUBLIC_KEY', 'VAPID_PRIVATE_KEY', 'VAPID_CLAIMS_SUBJECT')

@register()
def vapid_settings_check(app_configs, **kwargs):
    errors = []
    for name in VAPID_SETTING_NAMES:
        val = getattr(settings, name, None)
        if not val:
            errors.append(
                Error(
                    f'Missing {name}',
                    hint=f'Add {name} to your settings or environment (e.g. via .env).',
                    id=f'core.E001'
                )
            )
    return errors
