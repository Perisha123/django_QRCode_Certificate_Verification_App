from django import forms
from .models import Certificate

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'email', 'file']  # no need to include file_hash or qr_code