from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
import io
from PIL import Image

from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Create an Arabic blog post for testing (تحسين-الإنتاجية)'

    def handle(self, *args, **options):
        slug = 'تحسين-الإنتاجية'
        title_ar = 'طرق فعّالة لتحسين إنتاجيتك اليومية'
        content_ar = (
            'تعتبر إدارة الوقت وتنظيم المهام من أهم العوامل التي تساعد على زيادة الإنتاجية اليومية. '\
            'في هذا المقال، سنستعرض خمس استراتيجيات عملية يمكن تطبيقها فورًا:\n\n'
            '1. **وضع خطة يومية:** ابدأ يومك بكتابة قائمة المهام الأكثر أهمية، ورتبها حسب الأولوية.  \n'
            '2. **تقنية البومودورو:** استخدم فترات تركيز قصيرة (25 دقيقة) ثم استراحة قصيرة (5 دقائق) لتحافظ على نشاطك.  \n'
            '3. **التخلص من المشتتات:** أغلق الإشعارات غير الضرورية وحدد أوقاتًا محددة لتفقد البريد الإلكتروني.  \n'
            '4. **ممارسة الرياضة:** النشاط البدني يحسن التركيز ويقلل التوتر.  \n'
            '5. **تقييم يومك:** في نهاية اليوم، راجع ما أنجزته وحدد المهام التي تحتاج إلى إعادة ترتيب.\n\n'
            'باتباع هذه الاستراتيجيات البسيطة، ستلاحظ تحسنًا ملموسًا في إنتاجيتك اليومية وقدرتك على إدارة وقتك بشكل أفضل.'
        )

        post, created = BlogPost.objects.get_or_create(slug=slug)
        post.set_current_language('ar')
        post.title = title_ar
        post.content = content_ar
        post.published_at = timezone.now()

        # Attach a tiny placeholder featured image if none exists
        if not post.featured_image:
            img = Image.new('RGB', (1200, 800), color=(200, 200, 200))
            bio = io.BytesIO()
            img.save(bio, format='JPEG')
            bio.seek(0)
            post.featured_image.save('productivity.jpg', ContentFile(bio.read()), save=False)

        post.save()

        self.stdout.write(self.style.SUCCESS(f"Created post '{slug}' (created={created})"))
