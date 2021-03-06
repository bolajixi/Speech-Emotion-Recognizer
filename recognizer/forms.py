from django import forms
from django.forms import widgets
from recognizer.models import Audio_store


class AudioForm(forms.ModelForm):
    """Form definition for Audio."""

    class Meta:
        """Meta definition for Audioform."""

        model = Audio_store
        fields = ('record',)

        upload_styles = {'class': 'field__input', }
        widgets = {
            'record': forms.FileInput(attrs=upload_styles)
        }
