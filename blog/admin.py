from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from parler.admin import TranslatableAdmin
from .models import BlogPost
from .models import Comment
from .models import NotificationLog
from .models import LawyerCard
from django.conf import settings
from django.core.mail import send_mail


@admin.register(BlogPost)
class BlogPostAdmin(TranslatableAdmin):
    def og_image_tag(self, obj):
        # Prefer processed image for preview if available
        img_field = None
        if obj and getattr(obj, 'processed_og_image', None):
            img_field = obj.processed_og_image
        elif obj and getattr(obj, 'og_image', None):
            img_field = obj.og_image

        if img_field:
            try:
                url = img_field.url
                return mark_safe(f'<img src="{url}" style="max-height:100px;" />')
            except Exception:
                return ''
        return ''

    og_image_tag.short_description = 'OG معاينة'

    list_display = ('title', 'published_at', 'og_image_tag')
    readonly_fields = ('og_image_tag', 'processed_og_image_large', 'processed_og_image_medium', 'processed_og_image_small')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'published_at', 'featured_image')
        }),
        ('تعليمات صورة OG', {
            'classes': ('collapse',),
            'description': 'يفضل رفع صور بجودة عالية. المواصفات الموصى بها: 1200×630 بكسل (نسبة ~1.91:1)، صيغ JPG أو PNG، وحجم ≤ 5 ميغابايت. تُخلق نسخ معالجة تلقائيًا للاستخدام في بطاقات المشاركة.',
            'fields': ('og_image', 'og_image_tag')
        }),
        ('نسخ معالجة (للاطلاع)', {
            'fields': ('processed_og_image_large', 'processed_og_image_medium', 'processed_og_image_small')
        }),
        ('المحتوى', {
            'fields': ('content',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_post', 'short_comment', 'created_at', 'approved', 'approve_button')
    list_filter = ('approved', 'created_at')
    search_fields = ('name', 'email', 'comment', 'post__slug', 'post__translations__title')
    actions = ['approve_comments']

    def short_post(self, obj):
        return str(obj.post)
    short_post.short_description = 'المقال'

    def short_comment(self, obj):
        return (obj.comment[:75] + '...') if len(obj.comment) > 75 else obj.comment
    short_comment.short_description = 'النص'

    def approve_button(self, obj):
        if obj.approved:
            # Show delete button for already approved comments
            delete_url = reverse('admin:blog_comment_delete', args=[obj.pk])
            resend_url = reverse('admin:blog_comment_resend', args=[obj.pk])
            # include a short excerpt plus context in data attributes for the modal
            excerpt = (obj.comment[:200] + '...') if len(obj.comment) > 200 else obj.comment
            post_title = str(obj.post)
            commenter_email = obj.email or ''
            created_at = obj.created_at.isoformat() if getattr(obj, 'created_at', None) else ''
            return format_html('<a class="button resend-link" href="#" data-resend-url="{}" data-comment="{}" data-post-title="{}" data-email="{}" data-created-at="{}">إعادة إرسال</a>&nbsp; <a class="button btn-danger" href="{}">حذف</a>', resend_url, excerpt, post_title, commenter_email, created_at, delete_url)

        approve_url = reverse('admin:blog_comment_approve', args=[obj.pk])
        delete_url = reverse('admin:blog_comment_delete', args=[obj.pk])
        resend_url = reverse('admin:blog_comment_resend', args=[obj.pk])
        excerpt = (obj.comment[:200] + '...') if len(obj.comment) > 200 else obj.comment
        post_title = str(obj.post)
        commenter_email = obj.email or ''
        created_at = obj.created_at.isoformat() if getattr(obj, 'created_at', None) else ''
        return format_html(
            '<a class="button" href="{}">اعتمد</a>&nbsp; <a class="button resend-link" href="#" data-resend-url="{}" data-comment="{}" data-post-title="{}" data-email="{}" data-created-at="{}">إعادة إرسال</a>&nbsp; <a class="button btn-danger" href="{}">حذف</a>',
            approve_url, resend_url, excerpt, post_title, commenter_email, created_at, delete_url
        )
    approve_button.short_description = 'إجراء'

    class Media:
        # Load a small loader which prefers a local official bootstrap bundle
        # at /static/vendor/bootstrap.bundle.min.js, and falls back to CDN.
        js = ('vendor/bootstrap-loader.js', 'blog/js/admin-resend-modal.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/approve/', self.admin_site.admin_view(self.approve_view), name='blog_comment_approve'),
            path('<int:pk>/delete/', self.admin_site.admin_view(self.delete_view), name='blog_comment_delete'),
            path('<int:pk>/resend/', self.admin_site.admin_view(self.resend_comment_view), name='blog_comment_resend'),
        ]
        return custom_urls + urls

    def approve_view(self, request, pk):
        # Permission check
        if not self.has_change_permission(request):
            messages.error(request, 'لا تملك صلاحية اعطاء الموافقة')
            return redirect('..')

        comment = get_object_or_404(Comment, pk=pk)
        comment.approved = True
        comment.save(update_fields=['approved'])

        # Optional notification on approve/delete
        if getattr(settings, 'NOTIFY_ON_APPROVE_DELETE', True):
            recipient = getattr(settings, 'NOTIFY_EMAIL', None)
            if recipient:
                subject = f"✅ تم اعتماد تعليق جديد على {comment.post}"
                post_url = comment.post.get_absolute_url()
                message = f"تم اعتماد تعليق جديد على المقال: {comment.post}\n\nمن: {comment.name or 'زائر'}\n\n{comment.comment}\n\nعرض المقال: {post_url}"
                try:
                    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [recipient])
                    sent = True
                except Exception:
                    sent = False

                NotificationLog.objects.create(
                    notify_type='approved',
                    comment_text=comment.comment,
                    commenter_name=comment.name or '',
                    sent=sent,
                    related_comment=comment,
                )

        messages.success(request, 'تم اعتماد التعليق.')
        return redirect(reverse('admin:blog_comment_changelist'))

    def delete_view(self, request, pk):
        # Permission check
        if not self.has_delete_permission(request):
            messages.error(request, 'لا تملك صلاحية حذف التعليق')
            return redirect('..')

        comment = get_object_or_404(Comment, pk=pk)
        # Capture summary before deletion
        post_title = str(comment.post)
        comment_text = comment.comment[:200]
        comment.delete()

        if getattr(settings, 'NOTIFY_ON_APPROVE_DELETE', True):
            recipient = getattr(settings, 'NOTIFY_EMAIL', None)
            if recipient:
                subject = "🗑️ تم حذف تعليق"
                message = f"تم حذف تعليق على المقال: {post_title}\n\nملخص التعليق: {comment_text}"
                try:
                    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [recipient])
                    sent = True
                except Exception:
                    sent = False

                NotificationLog.objects.create(
                    notify_type='deleted',
                    comment_text=comment_text,
                    commenter_name=comment.name or '',
                    sent=sent,
                    related_comment=None,
                )

        messages.success(request, 'تم حذف التعليق بنجاح')
        return redirect(reverse('admin:blog_comment_changelist'))

    def resend_comment_view(self, request, pk):
        # Only allow POST to perform resend (prevents CSRF via GET/bookmark)
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        # Permission check
        if not self.has_change_permission(request):
            messages.error(request, 'لا تملك صلاحية إعادة الإرسال')
            return redirect('..')

        comment = get_object_or_404(Comment, pk=pk)

        # Require explicit confirmation token from POST to avoid accidental calls
        if request.POST.get('resend_confirm') != '1':
            messages.error(request, 'لم يتم تأكيد إعادة الإرسال')
            return redirect(reverse('admin:blog_comment_changelist'))

        recipient = getattr(settings, 'NOTIFY_EMAIL', None)
        if not recipient:
            messages.error(request, 'لم يتم إعداد بريد الإشعارات')
            return redirect(reverse('admin:blog_comment_changelist'))

        if comment.approved:
            # Send approved-style notification
            subject = f"✅ تم اعتماد تعليق جديد على {comment.post}"
            post_url = comment.post.get_absolute_url()
            message = f"تم اعتماد تعليق جديد على المقال: {comment.post}\n\nمن: {comment.name or 'زائر'}\n\n{comment.comment}\n\nعرض المقال: {post_url}"
            notify_type = 'approved'
        else:
            # Send created-style notification (include admin link)
            domain = getattr(settings, 'SITE_DOMAIN', None)
            if not domain:
                allowed = getattr(settings, 'ALLOWED_HOSTS', [])
                domain = allowed[0] if allowed else 'example.com'
            admin_url = f'https://{domain}' + reverse('admin:blog_comment_change', args=[comment.pk])
            subject = 'تعليق جديد قيد المراجعة'
            message = f"وصول تعليق جديد على المقال: {comment.post}\n\nمن: {comment.name or 'زائر'}\n\n{comment.comment}\n\nراجع التعليق هنا: {admin_url}"
            notify_type = 'created'

        try:
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [recipient])
            sent = True
        except Exception:
            sent = False

        NotificationLog.objects.create(
            notify_type=notify_type,
            comment_text=comment.comment,
            commenter_name=comment.name or '',
            sent=sent,
            related_comment=comment if notify_type != 'deleted' else None,
        )

        if sent:
            messages.success(request, 'تم إعادة إرسال الإشعار')
        else:
            messages.error(request, 'فشل إرسال الإشعار')

        return redirect(reverse('admin:blog_comment_changelist'))

    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"تم اعتماد {updated} تعليق(ات)")
    approve_comments.short_description = 'اعتمد التعليقات المحددة'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notify_type', 'commenter_name', 'created_at', 'sent')
    list_filter = ('notify_type', 'created_at', 'sent')
    search_fields = ('comment_text', 'commenter_name')
    actions = ['resend_notifications']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/resend/', self.admin_site.admin_view(self.resend_view), name='blog_notificationlog_resend'),
        ]
        return custom_urls + urls

    def resend_view(self, request, pk):
        if not self.has_change_permission(request):
            messages.error(request, 'لا تملك صلاحية إعادة الإرسال')
            return redirect('..')

        log = get_object_or_404(NotificationLog, pk=pk)
        sent = self._resend_log(log)
        if sent:
            messages.success(request, 'تم إعادة إرسال الإشعار')
        else:
            messages.error(request, 'فشل إعادة الإرسال')
        return redirect(reverse('admin:blog_notificationlog_changelist'))

    def resend_notifications(self, request, queryset):
        sent_count = 0
        for log in queryset:
            if self._resend_log(log):
                sent_count += 1
        self.message_user(request, f"تمت إعادة إرسال {sent_count} إشعار(ات)")
    resend_notifications.short_description = 'أعد إرسال الإشعارات المحددة'

    def _resend_log(self, log):
        """Attempt to resend the given NotificationLog. Create a new NotificationLog entry for the resend and
        mark original as sent=True if successful."""
        recipient = getattr(settings, 'NOTIFY_EMAIL', None)
        if not recipient:
            return False

        subject = ''
        message = ''

        if log.notify_type == 'created':
            subject = 'تعليق جديد قيد المراجعة'
            # try to include admin link for the related comment
            if log.related_comment:
                domain = getattr(settings, 'SITE_DOMAIN', None)
                if not domain:
                    allowed = getattr(settings, 'ALLOWED_HOSTS', [])
                    domain = allowed[0] if allowed else 'example.com'
                admin_url = f'https://{domain}' + reverse('admin:blog_comment_change', args=[log.related_comment.pk])
                message = f"وصول تعليق جديد على المقال: {log.related_comment.post}\n\nمن: {log.commenter_name or 'زائر'}\n\n{log.comment_text}\n\nراجع التعليق هنا: {admin_url}"
            else:
                message = f"وصول تعليق جديد\n\n{log.comment_text}"
        elif log.notify_type == 'approved':
            subject = f"✅ تم اعتماد تعليق جديد على {log.related_comment.post if log.related_comment else ''}"
            post_url = log.related_comment.post.get_absolute_url() if log.related_comment else ''
            message = f"تم اعتماد تعليق جديد على المقال: {log.related_comment.post if log.related_comment else ''}\n\nمن: {log.commenter_name or 'زائر'}\n\n{log.comment_text}\n\nعرض المقال: {post_url}"
        elif log.notify_type == 'deleted':
            subject = '🗑️ تم حذف تعليق'
            message = f"تم حذف تعليق على المقال: {log.comment_text}\n\nملخص التعليق: {log.comment_text}"
        else:
            return False

        try:
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), [recipient])
            sent = True
        except Exception:
            sent = False

        # Update original log and create a new log for the resend
        log.sent = log.sent or sent
        log.save(update_fields=['sent'])

        NotificationLog.objects.create(
            notify_type=log.notify_type,
            comment_text=log.comment_text,
            commenter_name=log.commenter_name,
            sent=sent,
            related_comment=log.related_comment,
        )

        return sent


@admin.register(LawyerCard)
class LawyerCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order', 'created_at', 'admin_thumbnail')
    list_filter = ('is_active',)
    search_fields = ('name', 'bio')
    readonly_fields = ('admin_thumbnail',)
    ordering = ('order', '-created_at')

    fieldsets = (
        (None, {'fields': ('name', 'bio', 'image')}),
        ('خيارات العرض', {'fields': ('is_active', 'order')}),
    )
