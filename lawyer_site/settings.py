import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me')

DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()
# Ensure PythonAnywhere host is allowed (case-insensitive match)
if 'loayalzaben.pythonanywhere.com' not in [h.lower() for h in ALLOWED_HOSTS]:
    ALLOWED_HOSTS.append('loayalzaben.pythonanywhere.com')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'parler',
    'crispy_forms',
    'django_extensions',
    # local apps
    'core',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lawyer_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lawyer_site.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'lawyer_site.wsgi.application'

# Database (SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ar'

TIME_ZONE = 'Asia/Amman'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

# Explicitly declare supported languages for Django
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

PARLER_LANGUAGES = {
    None: (
        {'code': 'ar'},
        {'code': 'en'},
    ),
    'default': {
        'fallbacks': ['ar'],
        'hide_untranslated': False,
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Directory where `collectstatic` will collect static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Site-wide settings
SITE_NAME = os.getenv('SITE_NAME', 'المحامية إيمان النجار')
SITE_NAME_EN = os.getenv('SITE_NAME_EN', 'Eman Al-Najjar')
SITE_DESCRIPTION = os.getenv('SITE_DESCRIPTION', 'مكتب محاماة يقدم استشارات وتمثيل قانوني شخصي ومهني.')

# Optional contact/provider metadata (used for JSON-LD and SEO). These can be
# configured via environment variables in production. These conservative
# placeholders are safe for local testing and should be replaced with real
# values before deploying.
SITE_PHONE = os.getenv('SITE_PHONE', '+962-7xx-xxx-xxx')
SITE_LOGO = os.getenv('SITE_LOGO', '/static/img/logo.png')
SITE_SAMEAS = os.getenv('SITE_SAMEAS', 'https://www.facebook.com/example')
# SITE_ADDRESS can be a simple string or a JSON/dict-like string if you prefer structured address
SITE_ADDRESS = os.getenv('SITE_ADDRESS', 'شارع المثال، عمان، الأردن')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Email (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# Security settings - enable stricter defaults when DEBUG is False or via env
# These can be tuned via environment variables in production.
USE_X_FORWARDED_PROTO = os.getenv('USE_X_FORWARDED_PROTO', '0') == '1'
if USE_X_FORWARDED_PROTO:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Default HSTS to 0 in DEBUG, otherwise set from env (seconds)
if DEBUG:
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', '1') == '1'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', '1') == '1'
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', '1') == '1'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', '1') == '1'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', '1') == '1'

# Additional browser security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = os.getenv('X_FRAME_OPTIONS', 'DENY')

