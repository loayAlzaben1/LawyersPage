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
