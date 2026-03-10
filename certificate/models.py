from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    # uploaded certificate file
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

    # SHA256 hash
    file_hash = models.CharField(max_length=64)

    # generated QR code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    # timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name