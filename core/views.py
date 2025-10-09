from django.shortcuts import render, redirect
from .models import Service, Case, SiteStats, Category, Tag
# blog app removed: avoid direct imports. We'll attempt an import at runtime to keep backward compatibility.
try:
    from blog.models import LawyerCard, BlogPost  # type: ignore
except Exception:
    LawyerCard = None
    BlogPost = None
from .forms import AppointmentForm, ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import F
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import HttpResponse
from .models import WebPushSubscription
import base64


def home(request):
    services = Service.objects.all().order_by('order')
    # Prefer rich LawyerProfile in core.models; fall back to lightweight LawyerCard if available
    try:
        from .models import LawyerProfile
    except Exception:
        LawyerProfile = None

    lawyers = []
    # Prefer core.LawyerProfile if it exists and has entries; otherwise fall back
    # to the legacy blog.LawyerCard (if available). This avoids a situation
    # where an empty LawyerProfile table prevents showing active LawyerCard
    # records that may exist on deployed sites.
    try:
        if LawyerProfile and LawyerProfile.objects.exists():
            lawyers = LawyerProfile.objects.all()[:12]
        elif LawyerCard and LawyerCard.objects.filter(is_active=True).exists():
            lawyers = LawyerCard.objects.filter(is_active=True).order_by('order')[:12]
    except Exception:
        # If anything goes wrong querying the DB, fall back to an empty list
        lawyers = []
    if BlogPost:
        latest_posts = BlogPost.objects.filter(published_at__isnull=False).order_by('-published_at')[:3]
    else:
        latest_posts = []

    site_stats = None
    try:
        site_stats = SiteStats.objects.first()
    except Exception:
        site_stats = None

    context = {
        'services': services,
        'lawyers': lawyers,
        'latest_posts': latest_posts,
        'site_stats': site_stats,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def services_list(request):
    services = Service.objects.all().order_by('order')
    return render(request, 'core/services.html', {'services': services})


def faq(request):
    faqs = [
        {'q': 'كم تكلفة الاستشارة؟', 'a': 'تختلف التكلفة حسب نوع القضية وطول الجلسة. الرجاء استخدام نموذج الحجز للحصول على تقدير.'},
        {'q': 'هل تتوفر استشارات عبر الإنترنت؟', 'a': 'نعم، تتوفر استشارات عبر مكالمة فيديو بعد تحديد موعد.'},
        {'q': 'كيف أرفع مستند لمراجعة القضية؟', 'a': 'أثناء حجز الموعد يمكنك رفع مرفق بصيغة PDF أو صورة. يُنصح بضغط الملفات الكبيرة.'},
    ]
    return render(request, 'core/faq.html', {'faqs': faqs})


def appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save()
            subject = f"New appointment from {appointment.name}"
            message = appointment.message or 'No message provided.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            return redirect('core:home')
    else:
        # Prefill the 'service' field if a service identifier is passed via GET.
        initial = {}
        svc = request.GET.get('service')
        if svc:
            # Try to resolve by numeric id first, otherwise try slug
            try:
                # numeric id
                sid = int(svc)
                from .models import Service
                s = Service.objects.filter(pk=sid).first()
            except Exception:
                from .models import Service
                s = Service.objects.filter(slug=svc).first()
            if s:
                initial['service'] = s.pk
                # Prefill a helpful message referencing the selected service
                try:
                    initial['message'] = (
                        f"أود حجز موعد للخدمة: {s.title}\n"
                        "التواريخ/الأوقات المفضلة: [مثال: 2025-09-25 صباحاً أو 2025-09-26 14:30]\n"
                        "ملاحظات إضافية: [اكتب ملخصًا موجزًا هنا]"
                    )
                except Exception:
                    initial['message'] = (
                        "أود حجز موعد - الرجاء التواصل لتحديد موعد.\n"
                        "التواريخ المفضلة: [اكتب هنا]\n"
                        "ملاحظات إضافية: [اكتب ملخصًا موجزًا هنا]"
                    )
        form = AppointmentForm(initial=initial)
    return render(request, 'core/appointment.html', {'form': form})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            subject = f"Contact message from {contact.name}"
            send_mail(subject, contact.message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def cases_view(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    qs = Case.objects.filter(published=True).order_by('-case_date', '-created_at')
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    if category:
        qs = qs.filter(category__name=category)
    if tag:
        qs = qs.filter(tag__name=tag) | qs.filter(tag__in=[tag])

    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        cases_page = paginator.page(page)
    except PageNotAnInteger:
        cases_page = paginator.page(1)
    except EmptyPage:
        cases_page = paginator.page(paginator.num_pages)

    count = qs.count()
    categories = Category.objects.all()
    tags = Tag.objects.all()

    current = cases_page.number
    total = paginator.num_pages
    start = max(1, current - 2)
    end = min(total, current + 2)
    page_numbers = list(range(start, end + 1))

    liked_cases = set(int(x) for x in request.session.get('liked_cases', []) if str(x).isdigit())

    context = {
        'cases': cases_page,
        'count': count,
        'paginator': paginator,
        'categories': categories,
        'tags': tags,
        'active_category': category,
        'active_tag': tag,
        'page_numbers': page_numbers,
        'liked_cases': liked_cases,
    }
    return render(request, 'core/cases.html', context)


def case_detail(request, pk):
    c = Case.objects.filter(pk=pk, published=True).first()
    if not c:
        raise Http404()
    liked_cases = set(int(x) for x in request.session.get('liked_cases', []) if str(x).isdigit())
    return render(request, 'core/case_detail.html', {'case': c, 'liked_cases': liked_cases})


def lawyer_detail(request, pk):
    """Show a lawyer profile.

    Prefer the richer `LawyerProfile` model in `core`. If it's not present, fall
    back to the lightweight `LawyerCard` (if available).
    """
    # Try core.LawyerProfile first
    try:
        from .models import LawyerProfile
    except Exception:
        LawyerProfile = None

    profile = None
    if LawyerProfile:
        profile = LawyerProfile.objects.filter(pk=pk).first()

    if not profile:
        # Fall back to LawyerCard (imported earlier if available)
        if LawyerCard:
            profile = LawyerCard.objects.filter(pk=pk, is_active=True).first()

    if not profile:
        raise Http404()

    return render(request, 'core/lawyer_detail.html', {'lawyer': profile})


@require_http_methods(["GET"])
def vapid_public_key(request):
    """Return the VAPID public key (base64) to the frontend so it can subscribe."""
    key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
    if not key:
        return HttpResponse(status=404)
    return HttpResponse(key)


@csrf_exempt
@require_POST
def save_subscription(request):
    """Save a push subscription posted from the browser.

    Expected JSON body: { endpoint: ..., keys: { p256dh: ..., auth: ... } }
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        endpoint = data.get('endpoint')
        keys = data.get('keys') or {}
        p256dh = keys.get('p256dh')
        auth_key = keys.get('auth')
        if not endpoint or not p256dh or not auth_key:
            return JsonResponse({'error': 'invalid_subscription'}, status=400)
        sub, created = WebPushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={'p256dh': p256dh, 'auth': auth_key}
        )
        return JsonResponse({'status': 'ok', 'created': created})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_subscription(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        endpoint = data.get('endpoint')
        if not endpoint:
            return JsonResponse({'error': 'missing_endpoint'}, status=400)
        WebPushSubscription.objects.filter(endpoint=endpoint).delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def toggle_like(request):
    """Handle like/unlike actions.

    Accepts either:
      - form-encoded POST with case_id and optional action (like/unlike)
      - application/json body containing a dict or array of {case_id, action}

    Returns JSON with authoritative counts.
    """
    liked_list = request.session.get('liked_cases', [])
    if not isinstance(liked_list, list):
        try:
            liked_list = list(liked_list)
        except Exception:
            liked_list = []
    liked_set = set(str(x) for x in liked_list)

    processed = []

    def apply_action_item(cid, action=None):
        cid = str(cid)
        try:
            case_obj = Case.objects.get(pk=cid)
        except Case.DoesNotExist:
            return None

        if action not in ('like', 'unlike'):
            want_like = cid not in liked_set
        else:
            want_like = (action == 'like')

        if want_like:
            if cid not in liked_set:
                Case.objects.filter(pk=cid).update(likes=F('likes') + 1)
                case_obj.refresh_from_db(fields=['likes'])
                liked_set.add(cid)
        else:
            if cid in liked_set:
                Case.objects.filter(pk=cid).update(likes=F('likes') - 1)
                case_obj.refresh_from_db(fields=['likes'])
                if case_obj.likes < 0:
                    case_obj.likes = 0
                    case_obj.save(update_fields=['likes'])
                liked_set.discard(cid)

        processed.append({'case_id': cid, 'liked': cid in liked_set, 'likes': case_obj.likes})
        return True

    # Try parse JSON body
    ct = request.content_type or ''
    if 'application/json' in ct:
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body) if body else None
            if isinstance(data, dict):
                cid = data.get('case_id') or data.get('caseId') or data.get('id')
                apply_action_item(cid, data.get('action'))
            elif isinstance(data, list):
                for item in data:
                    try:
                        cid = item.get('case_id') or item.get('caseId') or item.get('id')
                        apply_action_item(cid, item.get('action'))
                    except Exception:
                        continue
        except Exception:
            pass
    else:
        case_id = request.POST.get('case_id')
        action = request.POST.get('action')
        if not case_id:
            return JsonResponse({'error': 'missing case_id'}, status=400)
        apply_action_item(case_id, action)

    request.session['liked_cases'] = list(liked_set)

    if len(processed) == 1:
        return JsonResponse(processed[0])
    return JsonResponse({'results': processed, 'liked_cases': list(liked_set)})
