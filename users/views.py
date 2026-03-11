from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import qrcode
import os
from django.utils.crypto import get_random_string
from qrcode.constants import ERROR_CORRECT_H

# Import Certificate model and form
from certificate.models import Certificate
from certificate.forms import CertificateForm


# -------------------------
# User access page (Login/Register selection)
# -------------------------
def users_access(request):
    if request.user.is_authenticated:
        return redirect('users_dashboard')
    return render(request, "users_access.html")


# -------------------------
# User registration
# -------------------------
def users_register(request):
    if request.user.is_authenticated:
        return redirect('users_dashboard')

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect('users_register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('users_register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('users_register')

        user = User.objects.create_user(
            username=email, email=email, password=password, first_name=name
        )
        user.is_active = True
        user.save()

        send_mail(
            'Welcome to Blockchain Certificate Verification System',
            f'Hi {name}, your account has been created successfully!',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        messages.success(request, "Registration successful. Please log in.")
        return redirect('users_login')

    return render(request, "users_register.html")


# -------------------------
# User login
# -------------------------
def users_login(request):
    if request.user.is_authenticated:
        return redirect('users_dashboard')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return redirect('users_login')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('users_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('users_login')

    return render(request, "users_login.html")


# -------------------------
# User dashboard
# -------------------------
@login_required(login_url='users_login')
def users_dashboard(request):
    """User dashboard showing uploaded certificates"""
    certificates = Certificate.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "users_dashboard.html", {'certificates': certificates})


# -------------------------
# Upload certificate
# -------------------------
@login_required(login_url='users_login')
def upload_certificate(request):
    """Upload certificate and generate QR code"""
    show_qr = None

    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)

            # Generate SHA256 hash
            file_obj = request.FILES['file']
            file_data = file_obj.read()
            hash_value = hashlib.sha256(file_data).hexdigest()
            file_obj.seek(0)
            certificate.file_hash = hash_value

            # Assign logged-in user
            certificate.uploaded_by = request.user

            certificate.save()

            # Generate QR code
            random_suffix = get_random_string(6)
            filename = f"{hash_value}_{random_suffix}.png"
            qr_url = f"{request.scheme}://{request.get_host()}/verify/{hash_value}/"
            qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
            os.makedirs(qr_dir, exist_ok=True)
            qr_path = os.path.join(qr_dir, filename)

            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_path)

            certificate.qr_code.name = f"qr_codes/{filename}"
            certificate.save()

            messages.success(request, "Certificate uploaded successfully!")
            return redirect('users_dashboard')

    else:
        form = CertificateForm()

    return render(request, 'upload_certificate.html', {'form': form, 'show_qr': show_qr})


# -------------------------
# User logout
# -------------------------
@login_required(login_url='users_login')
def users_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')