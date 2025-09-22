from django.core.exceptions import ValidationError
from PIL import Image
import io


def validate_file_size(value):
    # limit to 10 MB
    limit = 10 * 1024 * 1024
    try:
        size = value.size
    except AttributeError:
        return
    if size > limit:
        raise ValidationError(f'حجم الملف أكبر من المسموح به ({limit // (1024*1024)}MB)')


def validate_file_extension(value):
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    name = getattr(value, 'name', '')
    if not name:
        return
    ext = name[name.rfind('.'):].lower()
    if ext not in allowed_extensions:
        raise ValidationError('نوع الملف غير مسموح به. مسموح: PDF, JPG, PNG')


def validate_og_image(value):
    """Strict validator for OG images.

    Rules:
    - Allowed extensions: .jpg, .jpeg, .png
    - Max size: 5 MB
    - Minimum dimensions: 1200x630 (recommended for social cards)
    - Aspect ratio tolerance: +/- 10% around 1200/630
    """
    # Allowed extensions
    name = getattr(value, 'name', '')
    if not name:
        raise ValidationError('الملف المرفوع غير صالح')
    ext = name[name.rfind('.') :].lower()
    if ext not in ('.jpg', '.jpeg', '.png'):
        raise ValidationError('يجب أن تكون صورة بصيغة JPG أو PNG للـ OG image.')

    # Size check (5 MB)
    limit = 5 * 1024 * 1024
    try:
        size = value.size
    except AttributeError:
        size = None
    if size and size > limit:
        raise ValidationError(f'حجم الصورة أكبر من المسموح به ({limit // (1024*1024)} ميغابايت).')

    # Dimension and aspect ratio check
    try:
        # Some UploadedFile objects don't support .read() after validation; use BytesIO
        file_bytes = value.read()
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
    except Exception:
        raise ValidationError('لا يمكن قراءة الصورة. تأكد من أنها ملف صورة صالح.')

    min_width, min_height = 1200, 630
    if width < min_width or height < min_height:
        raise ValidationError(f'أبعاد الصورة صغيرة جدًا؛ الحد الأدنى الموصى به هو {min_width}x{min_height} بكسل.')

    # Aspect ratio tolerance
    target_ratio = min_width / min_height
    ratio = width / height if height else 0
    tol = 0.10  # 10%
    if not (target_ratio * (1 - tol) <= ratio <= target_ratio * (1 + tol)):
        raise ValidationError('نسبة العرض إلى الارتفاع للصورة لا تتوافق مع متطلبات بطاقة المشاركة الاجتماعية. يرجى استخدام نسبة قريبة من 1200:630.')

