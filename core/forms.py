from django import forms
from .models import Appointment, ContactMessage, Service
from .validators import validate_file_size, validate_file_extension


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'phone', 'email', 'service', 'preferred_datetime', 'message', 'attachment']
        labels = {
            'name': 'الاسم',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'service': 'الخدمة',
            'preferred_datetime': 'التاريخ والوقت المفضل',
            'message': 'وصف المشكلة',
            'attachment': 'مرفق (PDF، صورة)'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'preferred_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'placeholder': 'مثال: 2025-09-17 14:30', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'اكتب وصفًا مختصرًا للمشكلة...', 'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            validate_file_size(attachment)
            validate_file_extension(attachment)
        return attachment


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        labels = {
            'name': 'الاسم',
            'email': 'البريد الإلكتروني',
            'phone': 'الهاتف',
            'subject': 'الموضوع',
            'message': 'الرسالة'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'اكتب رسالتك هنا...', 'class': 'form-control'}),
        }

    # simple honeypot field (not saved to model)
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('honeypot'):
            raise forms.ValidationError('Spam detected.')
        return cleaned
