# certificate/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if not User.objects.filter(username="adminuser").exists():
        User.objects.create_superuser(
            username="adminuser",
            email="perishadharela@gmail.com",
            password="Admin@123"
        )
        print("Default admin created!")