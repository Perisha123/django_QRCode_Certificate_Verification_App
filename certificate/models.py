from django.db import models
import hashlib
import qrcode
from io import BytesIO
from django.core.files import File

class Certificate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    file = models.FileField(upload_to='certificates/')
    file_hash = models.CharField(max_length=64, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # <-- add this

    def save(self, *args, **kwargs):
        if self.file:
            sha256 = hashlib.sha256()
            for chunk in self.file.chunks():
                sha256.update(chunk)
            self.file_hash = sha256.hexdigest()

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(self.file_hash)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f"{self.name}_qr.png"
            self.qr_code.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name