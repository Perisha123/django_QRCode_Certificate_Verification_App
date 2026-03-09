import hashlib
import qrcode
import os

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .models import Certificate
from .forms import CertificateForm

# --------------------------------------
# HOME PAGE
# --------------------------------------
def home(request):
    return render(request, 'home.html')


# --------------------------------------
# ADMIN LOGIN
# --------------------------------------
def admin_login(request):
    # --- Ensure default admin exists (run once at server start) ---

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:  # only allow staff/admin
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'admin_login.html')


# --------------------------------------
# ADMIN LOGOUT
# --------------------------------------
@login_required
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('admin_login')


# --------------------------------------
# ADMIN DASHBOARD
# --------------------------------------
@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied: Admins only.")
        return redirect('home')

    certificates = Certificate.objects.all().order_by('-created_at')
    total = certificates.count()

    return render(request, 'admin_dashboard.html', {
        'certificates': certificates,
        'total': total
    })


# --------------------------------------
# UPLOAD CERTIFICATE
# --------------------------------------
@login_required
def upload_certificate(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied: Admins only.")
        return redirect('home')

    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)

        if form.is_valid():
            certificate = form.save(commit=False)
            file = request.FILES['certificate_file']

            # generate SHA256 hash
            hash_value = hashlib.sha256(file.read()).hexdigest()
            certificate.file_hash = hash_value
            certificate.save()

            # ensure qr_codes folder exists
            qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
            os.makedirs(qr_dir, exist_ok=True)

            # create QR code
            verify_url = f"http://127.0.0.1:8000/verify/{hash_value}"
            qr = qrcode.make(verify_url)
            qr_path = os.path.join(qr_dir, f"{hash_value}.png")
            qr.save(qr_path)

            certificate.qr_code = f"qr_codes/{hash_value}.png"
            certificate.save()

            messages.success(request, "Certificate uploaded successfully!")
            return render(request, 'result.html', {
                'certificate': certificate,
                'hash': hash_value
            })
    else:
        form = CertificateForm()

    return render(request, 'upload_certificate.html', {'form': form})


# --------------------------------------
# VERIFY CERTIFICATE
# --------------------------------------
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