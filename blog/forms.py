from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    # Honeypot field - should remain empty in legitimate submissions
    hp_field = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ['name', 'email', 'comment', 'hp_field']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        hp = cleaned.get('hp_field')
        if hp:
            # Honeypot filled -> treat as spam
            raise forms.ValidationError('Spam detected')
        return cleaned