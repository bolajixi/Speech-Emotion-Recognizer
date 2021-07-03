from django import forms
from recognizer.models import Audio_store


class AudioForm(forms.ModelForm):
    """Form definition for Audio."""

    class Meta:
        """Meta definition for Audioform."""

        model = Audio_store
        fields = ('record',)
