"""Find blog posts that have no featured image and no processed OG images."""
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_site.settings')
import django
django.setup()

from blog.models import BlogPost

missing = []
for p in BlogPost.objects.all():
    has_featured = bool(getattr(p, 'featured_image') and getattr(p, 'featured_image').name)
    has_processed = any([
        getattr(p, 'processed_og_image_small'),
        getattr(p, 'processed_og_image_medium'),
        getattr(p, 'processed_og_image_large'),
    ])
    if not has_featured and not has_processed:
        missing.append((p.pk, getattr(p, 'slug', None), p.title))

print('posts missing images:', missing)
