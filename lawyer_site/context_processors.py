def site_settings(request):
    """Expose simple site settings to templates."""
    from django.conf import settings
    # pick site name according to current language (fall back to Arabic)
    from django.utils import translation
    lang = getattr(request, 'LANGUAGE_CODE', None) or translation.get_language()
    if lang and lang.startswith('en'):
        name = getattr(settings, 'SITE_NAME_EN', getattr(settings, 'SITE_NAME', 'المحامية إيمان النجار'))
    else:
        name = getattr(settings, 'SITE_NAME', 'المحامية إيمان النجار')
    return {
        'SITE_NAME': name,
        'SITE_NAME_AR': getattr(settings, 'SITE_NAME', 'المحامية إيمان النجار'),
        'SITE_NAME_EN': getattr(settings, 'SITE_NAME_EN', 'Eman Al-Najjar'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'مكتب محاماة يقدم استشارات وتمثيل قانوني شخصي ومهني.'),
        # expose VAPID public key for client registration (may be None in dev until set)
        'VAPID_PUBLIC_KEY': getattr(settings, 'VAPID_PUBLIC_KEY', None),
    }
