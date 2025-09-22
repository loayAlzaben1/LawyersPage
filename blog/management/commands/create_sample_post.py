from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import BlogPost

class Command(BaseCommand):
    help = 'Create a sample bilingual blog post (Arabic/English)'

    def handle(self, *args, **options):
        slug = 'مثال-شعبي'  # Arabic slug
        post, created = BlogPost.objects.get_or_create(slug=slug)
        # Set translations using parler API
        post.set_current_language('ar')
        post.title = 'مثال شعبي'
        post.content = 'هذا مثال شعبي بسيط يعرض معلومات عامة بطريقة موجزة.'
        post.set_current_language('en')
        post.title = 'Popular Example'
        post.content = 'A short popular example with brief information.'
        post.published_at = timezone.now()
        post.save()
        self.stdout.write(self.style.SUCCESS(f"Created post '{slug}' (created={created})"))
