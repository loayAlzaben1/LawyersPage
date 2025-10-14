from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import LawyerProfile, Service, Appointment, ContactMessage
from .models import SiteStats
from .models import Case


@admin.register(LawyerProfile)
class LawyerProfileAdmin(TranslatableAdmin):
    list_display = ('full_name', 'email', 'phone')


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = ('title', 'order')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'service', 'preferred_datetime', 'status', 'created_at')
    list_filter = ('status', 'service')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    list_display = ('cases_won', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'case_type', 'outcome', 'published', 'created_at', 'admin_thumbnail')
    list_filter = ('published', 'case_type', 'outcome')
    search_fields = ('title', 'summary', 'client_initials')
    readonly_fields = ('admin_thumbnail',)
    fieldsets = (
        (None, {'fields': ('title', 'summary', 'image', 'admin_thumbnail', 'published')}),
        ('تفاصيل القضية', {'fields': ('case_type', 'outcome', 'case_date', 'client_initials')}),
    )


from django.utils.html import format_html
from django.contrib import admin
from .models import CaseDocument
from .models import Category, Tag, CaseImage
from .models import WebPushSubscription
from .utils import send_webpush
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


class CaseDocumentInline(admin.TabularInline):
    model = CaseDocument
    extra = 1
    readonly_fields = ('file_link',)
    fields = ('title', 'file', 'file_link')

    def file_link(self, obj):
        if not obj.file:
            return ''
        return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.name)

    file_link.short_description = 'رابط الملف'

CaseAdmin.inlines = [CaseDocumentInline]


class CaseImageInline(admin.TabularInline):
    model = CaseImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


CaseAdmin.inlines += [CaseImageInline]

CaseAdmin.list_display = ('title', 'case_type', 'outcome', 'published', 'case_date', 'client_initials', 'admin_thumbnail')
CaseAdmin.list_filter = ('published', 'case_type', 'outcome', 'case_date')
CaseAdmin.search_fields = ('title', 'summary', 'client_initials')


@admin.register(WebPushSubscription)
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('short_endpoint', 'user', 'created_at')
    readonly_fields = ('endpoint', 'p256dh', 'auth', 'user', 'created_at')
    actions = ('send_test_notification', 'attach_subscriptions_to_user',)

    def short_endpoint(self, obj):
        return (obj.endpoint[:80] + '...') if len(obj.endpoint) > 80 else obj.endpoint
    short_endpoint.short_description = 'Endpoint'

    def send_test_notification(self, request, queryset):
        """Admin action to enqueue a test notification to selected subscriptions via Celery/task.

        This uses `core.tasks.send_pushes_to_subscriptions` so sends are processed asynchronously
        when Celery and a broker are available.
        """
        try:
            from . import tasks as push_tasks
            ids = list(queryset.values_list('id', flat=True))
            task = getattr(push_tasks, 'send_pushes_to_subscriptions')
            if hasattr(task, 'delay'):
                task.delay(ids, None, 'Test Notification', 'This is a test notification from admin.', '/')
            else:
                task(ids, None, 'Test Notification', 'This is a test notification from admin.', '/')
            self.message_user(request, f'Enqueued test notification to {len(ids)} subscriptions.')
        except Exception as e:
            # Fallback: try to send synchronously
            sent = 0
            for s in queryset:
                info = {'endpoint': s.endpoint, 'keys': {'p256dh': s.p256dh, 'auth': s.auth}}
                ok = send_webpush(info, title='Test Notification', body='This is a test notification from admin.', url='/')
                if ok:
                    sent += 1
            self.message_user(request, f'Sent to {sent} of {queryset.count()} subscriptions (sync fallback).')
    send_test_notification.short_description = 'Send test notification to selected subscriptions'

    def attach_subscriptions_to_user(self, request, queryset):
        """Redirect to a small admin view where the admin can choose a user to attach the
        selected subscriptions to. We pass subscription ids via the query string.
        """
        ids = ','.join(str(x) for x in queryset.values_list('id', flat=True))
        from django.urls import reverse
        from django.shortcuts import redirect
        # Redirect to our WebPushSubscription admin attach view which will show a form to pick a user.
        url = reverse('admin:core_webpushsubscription_attach') + f'?attach_sub_ids={ids}'
        return redirect(url)

    attach_subscriptions_to_user.short_description = 'Attach selected subscriptions to a user (redirect)'

    # Add a custom admin view to show a small form where the admin picks a user and submits to attach.
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('attach/', self.admin_site.admin_view(self.attach_subscriptions_view), name='core_webpushsubscription_attach'),
        ]
        return custom_urls + urls

    def attach_subscriptions_view(self, request):
        """GET: render a form with a user select and hidden subscription ids.
        POST: attach the provided subscription ids to the chosen user.
        """
        from django.shortcuts import render, redirect
        from django.urls import reverse
        from django.contrib import messages
        User = get_user_model()

        if request.method == 'POST':
            user_id = request.POST.get('user_id')
            ids = request.POST.get('attach_sub_ids', '')
            try:
                sub_ids = [int(x) for x in ids.split(',') if x.strip()]
            except Exception:
                sub_ids = []

            if not sub_ids:
                messages.warning(request, 'No valid subscription ids provided.')
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:core_webpushsubscription_changelist')))

            try:
                user_obj = User.objects.get(pk=int(user_id)) if user_id else None
            except Exception:
                user_obj = None

            attached = WebPushSubscription.objects.filter(id__in=sub_ids).update(user=user_obj)
            messages.success(request, f'Attached {attached} subscriptions to user {user_obj}.')
            return redirect(request.META.get('HTTP_REFERER', reverse('admin:core_webpushsubscription_changelist')))

        # GET
        ids = request.GET.get('attach_sub_ids', '')
        try:
            sub_ids = [int(x) for x in ids.split(',') if x.strip()]
        except Exception:
            sub_ids = []

        users = get_user_model().objects.filter(is_active=True).order_by('username')[:200]
        context = {
            'subscriptions': WebPushSubscription.objects.filter(id__in=sub_ids),
            'attach_sub_ids': ids,
            'users': users,
            'opts': self.model._meta,
        }
        return render(request, 'admin/core/attach_subscriptions.html', context)


from .models import Notification
from .models import Review


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('name', 'text')
    readonly_fields = ('created_at',)


# Extend the built-in User admin to add an action for sending notifications to a user's subscriptions
try:
    User = get_user_model()
    # Unregister the existing User admin and register a custom one
    try:
        admin.site.unregister(User)
    except Exception:
        # If it wasn't registered yet, ignore
        pass

    class CustomUserAdmin(DjangoUserAdmin):
        actions = ('send_notification_to_user_subscriptions',)
        # use a custom change form template to add a "Send notification" button
        change_form_template = 'admin/core/user_change_form.html'

        def send_notification_to_user_subscriptions(self, request, queryset):
            """Admin action: send a test notification to selected users' subscriptions."""
            try:
                from . import tasks as push_tasks
                # collect subscription ids for selected users
                sub_ids = list(WebPushSubscription.objects.filter(user__in=queryset).values_list('id', flat=True))
                if not sub_ids:
                    self.message_user(request, 'No subscriptions found for selected users.')
                    return
                task = getattr(push_tasks, 'send_pushes_to_subscriptions')
                if hasattr(task, 'delay'):
                    task.delay(sub_ids, None, 'Message from admin', 'This is a test notification sent to the user.', '/')
                else:
                    task(sub_ids, None, 'Message from admin', 'This is a test notification sent to the user.', '/')
                self.message_user(request, f'Enqueued test notification to {len(sub_ids)} subscriptions.')
            except Exception:
                # Fallback: send synchronously
                sent = 0
                for s in WebPushSubscription.objects.filter(user__in=queryset):
                    info = {'endpoint': s.endpoint, 'keys': {'p256dh': s.p256dh, 'auth': s.auth}}
                    ok = send_webpush(info, title='Message from admin', body='This is a test notification sent to the user.', url='/')
                    if ok:
                        sent += 1
                self.message_user(request, f'Sent to {sent} subscriptions (sync fallback).')

        send_notification_to_user_subscriptions.short_description = 'Send test notification to selected users\' subscriptions'

        # Add a custom admin view to send a custom notification to a single user
        def get_urls(self):
            from django.urls import path
            urls = super().get_urls()
            custom_urls = [
                path('<path:object_id>/send_push/', self.admin_site.admin_view(self.send_push_view), name='core_user_send_push'),
                path('<path:object_id>/attach_subscriptions/', self.admin_site.admin_view(self.attach_subscriptions_view), name='core_user_attach_subscriptions'),
            ]
            return custom_urls + urls

        def send_push_view(self, request, object_id):
            """Admin view to send a custom notification to the user's subscriptions.

            Expects POST with 'title' and 'body'."""
            from django.shortcuts import redirect
            from django.urls import reverse
            from django.contrib import messages
            try:
                user_obj = User.objects.get(pk=object_id)
            except User.DoesNotExist:
                self.message_user(request, 'User not found.', level=messages.ERROR)
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_changelist')))

            if request.method == 'POST':
                title = request.POST.get('title') or 'Message from admin'
                body = request.POST.get('body') or ''
                # gather subscription ids
                sub_ids = list(WebPushSubscription.objects.filter(user=user_obj).values_list('id', flat=True))
                if not sub_ids:
                    self.message_user(request, 'No subscriptions for this user.', level=messages.WARNING)
                    return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))
                try:
                    from . import tasks as push_tasks
                    task = getattr(push_tasks, 'send_pushes_to_subscriptions')
                    if hasattr(task, 'delay'):
                        task.delay(sub_ids, None, title, body, '/')
                    else:
                        task(sub_ids, None, title, body, '/')
                    self.message_user(request, f'Enqueued notification to {len(sub_ids)} subscriptions.')
                except Exception:
                    # fallback synchronous
                    sent = 0
                    for s in WebPushSubscription.objects.filter(id__in=sub_ids):
                        info = {'endpoint': s.endpoint, 'keys': {'p256dh': s.p256dh, 'auth': s.auth}}
                        ok = send_webpush(info, title=title, body=body, url='/')
                        if ok:
                            sent += 1
                    self.message_user(request, f'Sent to {sent} subscriptions (sync fallback).')
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))

            # For non-POST just redirect back
            return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))

        def attach_subscriptions_view(self, request, object_id):
            """Attach subscriptions whose ids are passed in querystring param 'attach_sub_ids'.

            Example: /admin/auth/user/5/attach_subscriptions/?attach_sub_ids=1,2,3
            """
            from django.shortcuts import redirect
            from django.urls import reverse
            from django.contrib import messages
            try:
                user_obj = User.objects.get(pk=object_id)
            except User.DoesNotExist:
                self.message_user(request, 'User not found.', level=messages.ERROR)
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_changelist')))

            ids = request.GET.get('attach_sub_ids', '')
            if not ids:
                self.message_user(request, 'No subscription ids provided.', level=messages.WARNING)
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))
            try:
                sub_ids = [int(x) for x in ids.split(',') if x.strip()]
            except Exception:
                sub_ids = []

            if not sub_ids:
                self.message_user(request, 'No valid subscription ids provided.', level=messages.WARNING)
                return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))

            # perform update
            attached = WebPushSubscription.objects.filter(id__in=sub_ids).update(user=user_obj)
            self.message_user(request, f'Attached {attached} subscriptions to user {user_obj}.')
            return redirect(request.META.get('HTTP_REFERER', reverse('admin:auth_user_change', args=[object_id])))

    admin.site.register(User, CustomUserAdmin)
except Exception:
    # If user model isn't importable for any reason, skip adding the admin action
    pass
