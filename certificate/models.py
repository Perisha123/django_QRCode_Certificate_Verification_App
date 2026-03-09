from django.db import models
from django.contrib.auth.models import User

class Certificate(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    file = models.FileField(upload_to='certificates/')
    file_hash = models.CharField(max_length=64, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"