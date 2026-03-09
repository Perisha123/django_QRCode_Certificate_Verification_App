import hashlib
import qrcode
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Certificate
from .forms import CertificateForm


# --------------------------------------------------
# HOME PAGE
def home(request):
    return render(request, 'home.html')


# --------------------------------------------------
# ADMIN LOGIN
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            messages.success(request, "Welcome Admin!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'admin_login.html')


# --------------------------------------------------
# ADMIN LOGOUT
@login_required
def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('admin_login')


# --------------------------------------------------
# ADMIN DASHBOARD
@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Admins only can access this page")
        return redirect('home')

    certificates = Certificate.objects.order_by('-created_at')
    total = certificates.count()

    return render(request, 'admin_dashboard.html', {
        'certificates': certificates,
        'total': total
    })


# --------------------------------------------------
# UPLOAD CERTIFICATE
@login_required
def upload_certificate(request):
    if not request.user.is_staff:
        messages.error(request, "Admins only can upload")
        return redirect('home')

    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)

        if form.is_valid():
            certificate = form.save(commit=False)
            file_data = request.FILES['file'].read()
            hash_value = hashlib.sha256(file_data).hexdigest()
            certificate.file_hash = hash_value
            certificate.save()

            # Create QR code
            qr = qrcode.make(f"{request.scheme}://{request.get_host()}/verify/{hash_value}")
            qr_path = os.path.join(settings.MEDIA_ROOT, "qr_codes", f"{hash_value}.png")
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            qr.save(qr_path)
            certificate.qr_code.name = f"qr_codes/{hash_value}.png"
            certificate.save()

            messages.success(request, "Certificate uploaded!")
            return redirect('dashboard')

    else:
        form = CertificateForm()

    return render(request, 'upload_certificate.html', {'form': form})


# --------------------------------------------------
# VERIFY CERTIFICATE (User)
def verify_certificate(request, hash):
    try:
        certificate = Certificate.objects.get(file_hash=hash)
        status = "VALID CERTIFICATE"
    except Certificate.DoesNotExist:
        certificate = None
        status = "INVALID CERTIFICATE"

    return render(request, 'verify.html', {
        'status': status,
        'certificate': certificate
    })