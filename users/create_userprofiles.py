# users/create_userprofiles.py

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrverify.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

# Loop through all users
for user in User.objects.all():
    # Check if UserProfile exists; if not, create it
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'uploaded_by': user,  # or replace with a specific admin user
        }
    )
    if created:
        print(f"Created UserProfile for {user.username}")
    else:
        print(f"UserProfile already exists for {user.username}")

print("All user profiles checked/created ✅")