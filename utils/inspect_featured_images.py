"""Utility to inspect BlogPost featured_image fields and check media files on disk.
Run with: .venv\Scripts\python.exe utils\inspect_featured_images.py
"""
import os
import sys

# Ensure we run from project root
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()

from blog.models import BlogPost
from django.conf import settings

qs = BlogPost.objects.all()
print('MEDIA_ROOT=', settings.MEDIA_ROOT)
print('COUNT posts=', qs.count())

for p in qs:
    print('---')
    print('pk=', p.pk, 'slug=', getattr(p, 'slug', None))
    fi = getattr(p, 'featured_image', None)
    print('featured_image.name=', getattr(fi, 'name', None))
    try:
        print('url=', fi.url)
    except Exception as e:
        print('url error:', e)
    try:
        print('path=', fi.path)
        print('exists=', os.path.exists(fi.path))
    except Exception as e:
        print('path error:', e)

imgdir = os.path.join(str(settings.MEDIA_ROOT), 'blog_images')
if os.path.isdir(imgdir):
    print('media/blog_images files:', os.listdir(imgdir))
else:
    print('media/blog_images not found')
