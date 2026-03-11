import hashlib
import qrcode
import os

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.crypto import get_random_string
from qrcode.constants import ERROR_CORRECT_H

from .models import Certificate
from .forms import CertificateForm
from web3 import Web3  # Blockchain integration
# --------------------------------------------------
# CONNECT TO LOCAL BLOCKCHAIN (Ganache)
# --------------------------------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # Ganache default RPC
if w3.is_connected():
    print("Connected to Blockchain ✅")
else:
    print("Blockchain connection failed ❌")

# Example account to send transactions (Ganache pre-funded account)
default_account = w3.eth.accounts[0]
w3.eth.default_account = default_account

# --------------------------------------------------

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

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Welcome Admin!")
            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'admin_login.html')


# --------------------------------------------------
# ADMIN LOGOUT

@login_required(login_url='admin_login')
def admin_logout(request):

    logout(request)

    messages.success(request, "Logged out successfully")

    return redirect('admin_login')


# --------------------------------------------------
# ADMIN DASHBOARD

@staff_member_required(login_url='admin_login')
def dashboard(request):

    certificates = Certificate.objects.order_by('-created_at')

    total = certificates.count()

    return render(request, 'admin_dashboard.html', {
        'certificates': certificates,
        'total': total
    })


# --------------------------------------------------
# UPLOAD CERTIFICATE (User + Blockchain)
@login_required(login_url='users_login')
def upload_certificate(request):

    # Initialize variables so they exist on GET requests
    show_qr = None
    blockchain_status = None
    blockchain_status_class = None
    filename = None

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

            # Save uploaded user
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

            show_qr = certificate.qr_code.url

            # Record on Blockchain
            try:
                tx_hash = w3.eth.send_transaction({
                    'from': default_account,
                    'to': default_account,
                    'value': 0,
                    'data': hash_value.encode('utf-8')
                })
                w3.eth.wait_for_transaction_receipt(tx_hash)
                recorded_on_blockchain = True
            except Exception as e:
                print("Blockchain recording failed:", e)
                recorded_on_blockchain = False

            blockchain_status = "Recorded on Blockchain" if recorded_on_blockchain else "Not recorded"
            blockchain_status_class = "bg-success text-white" if recorded_on_blockchain else "bg-secondary text-white"

            messages.success(request, "Certificate uploaded successfully!")

            # Reset form
            form = CertificateForm()

    else:
        form = CertificateForm()

    return render(request, 'user_upload_certificate.html', {
        'form': form,
        'show_qr': show_qr,
        'qr_filename': filename if show_qr else None,
        'blockchain_status': blockchain_status,
        'blockchain_status_class': blockchain_status_class,
    })
# --------------------------------------------------
# VERIFY CERTIFICATE
def verify_certificate(request, file_hash):

    try:

        certificate = Certificate.objects.get(file_hash=file_hash)

        status = "VALID CERTIFICATE"

    except Certificate.DoesNotExist:

        certificate = None

        status = "INVALID CERTIFICATE"

    return render(request, 'verify.html', {
        'status': status,
        'certificate': certificate
    })
# --------------------------------------------------
# USER DASHBOARD

@login_required(login_url='users_login')
def users_dashboard(request):

    certificates = Certificate.objects.filter(uploaded_by=request.user)

    return render(request, 'users_dashboard.html', {
        'certificates': certificates
    })

@login_required(login_url='users_login')
def qr_scan(request):
    return render(request, 'qr_scan.html')
# --------------------------------------------------
# USER LOGOUT

@login_required(login_url='users_login')
def users_logout(request):

    logout(request)

    messages.success(request, "You have logged out successfully.")

    return redirect('home')   # goes to user portal home page