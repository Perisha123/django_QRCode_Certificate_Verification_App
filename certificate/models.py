from django.db import models

class Certificate(models.Model):

    student_name = models.CharField(max_length=200)

    course = models.CharField(max_length=200)

    certificate_file = models.FileField(upload_to='uploaded_certificates/')

    file_hash = models.CharField(max_length=256)

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_name