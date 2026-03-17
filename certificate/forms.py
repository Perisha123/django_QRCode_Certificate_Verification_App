from django import forms
from .models import Certificate
from django.contrib.auth.models import User


class CertificateForm(forms.ModelForm):
    # Admin chooses the user to assign certificate
    uploaded_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        label="Assign Certificate to",
        help_text="Select a user or check 'Assign to all"
    )

    class Meta:
        model = Certificate  # ← make sure this is set!
        fields = ['name', 'email', 'file']  # include the fields you want

