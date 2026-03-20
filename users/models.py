from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    title = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    file = models.FileField(upload_to='certificates/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_certificates')
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.CharField(max_length=42, default='0x0000000000000000000000000000000000000000')

    def __str__(self):
        return f"{self.title} ({self.uploaded_by.email})"