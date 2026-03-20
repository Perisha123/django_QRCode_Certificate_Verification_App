import hashlib
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_certificates'
    )
    uploaded_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificates_uploaded_by',
        null=True,
        blank=True
    )

    is_user_uploaded = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    # uploaded certificate file
    file = models.FileField(upload_to='certificates/', blank=True, null=True)
    

    # SHA256 hash
    file_hash = models.CharField(max_length=64, blank=True, editable=False)

    # generated QR code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    # timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Generate SHA256 hash if file exists and file_hash is empty
        if self.file and not self.file_hash:
            self.file.seek(0)
            data = self.file.read()
            self.file_hash = hashlib.sha256(data).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username if self.user else 'Nouser'}"