from django.db import models

class Certificate(models.Model):

    file = models.FileField(upload_to="certificates/")
    file_hash = models.CharField(max_length=256)

    blockchain_id = models.IntegerField(null=True, blank=True)

    tx_hash = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
# Create your models here.
