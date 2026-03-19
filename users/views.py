from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import qrcode
from .models import UserProfile
from io import BytesIO
from django.core.files import File
from django.shortcuts import get_object_or_404

import os
import json
from django.utils.crypto import get_random_string
from qrcode.constants import ERROR_CORRECT_H
from web3 import Web3
from django.conf import settings
from certificate.blockchain import user_certificates, verify_certificate, add_certificate_to_blockchain

# Import Certificate model and form
from certificate.models import Certificate
from certificate.forms import CertificateForm
from users.forms import UserCertificateUploadForm

# Connect to Ganache
# -----------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if w3.is_connected():
    print("Connected to Ganache!")
else:
    print("Failed to connect.")

# -----------------------------
# Load deployed contract ABI and bytecode
# -----------------------------
CONTRACT_ADDRESS = "0x2c61d671Dd1DbD60eB57672491E898f79Bf64ff0"  # Replace with your deployed contract

contract_path = os.path.join(
    settings.BASE_DIR,
    "blockchain",
    "contracts",
    "DocumentVerification.json"
)

with open(contract_path) as f:
    contract_json = json.load(f)

# Access the correct nested structure
contract_data = contract_json["contracts"]["DocumentVerification.sol"]["DocumentVerification"]
ABI = contract_data["abi"]
BYTECODE = contract_data["evm"]["bytecode"]["object"]

# -----------------------------
# Load contract instance
# -----------------------------
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

print("Contract loaded successfully!")
# -----------------------------
# View blockchain certificates
# -----------------------------
def view_certificates_blockchain(request):
    certificates = []
    try:
        total = contract.functions.counter().call()  # Get total stored documents
        for i in range(1, total + 1):
            doc = contract.functions.getDocument(i).call()
            certificates.append({
                "id": i,
                "file_hash": doc[0],
                "timestamp": doc[1],
                "owner": doc[2],
            })
    except Exception as e:
        print("Error fetching blockchain data:", e)

    return render(request, "users/blockchain_certificates.html", {"certificates": certificates})
# -------------------------
# User access page (Login/Register selection)
# -------------------------
def users_access(request):
    # Only staff/admins go to admin dashboard
    if request.user.is_staff:
        return redirect('users:dashboard')
    # Normal user sees user dashboard
    return render(request, 'users_access.html')

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
        return redirect('users:users_dashboard')

    return render(request, "users_register.html")


# -------------------------
# User login
# -------------------------

def users_login(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')  # user already logged in

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return redirect('users:login')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('users:login')

    return render(request, "users_login.html")
# -----------------------------
# Blockchain interaction helpers
# -----------------------------
def user_certificates(request):
    # Filter certificates uploaded by the logged-in user
    certificates = Certificate.objects.filter(uploaded_by=request.user)
    return render(request, 'users/user_uload_certificates.html', {'certificates': certificates})
def verify_certificate(cert_id):
    """Check if certificate ID exists on blockchain"""
    try:
        return contract.functions.verifyCertificate(cert_id).call()
    except Exception as e:
        print("Error verifying certificate:", e)
        return False
# -------------------------
# User dashboard
# -------------------------
from django.db.models import Q

@login_required(login_url='users_login')
def users_dashboard(request):
    # Certificates uploaded by the user OR assigned to the user
    user_certificates = Certificate.objects.filter(
        Q(uploaded_by_user=True, assigned_to=request.user) | Q(assigned_to=request.user) | Q(uploaded_by_user=True, assigned_to__isnull=True)
    ).order_by('-created_at')

    # Prepare list with blockchain status
    certs_with_status = []
    for cert in user_certificates:
        source = "You" if cert.uploaded_by_user == request.user else "Admin Assigned"

        blockchain_status = "Recorded on Blockchain" if cert.file_hash else "Not recorded"
        certs_with_status.append({
            'cert': cert,
            'blockchain_status': blockchain_status
        })

    return render(request, 'users_dashboard.html', {
        'certs_with_status': certs_with_status
    })

# Upload certificate
# -------------------------
@login_required(login_url='users_login')
def user_upload_certificate(request):
    message = None
    certificate = None

    if request.method == "POST":
        form = UserCertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.uploaded_by_user = True
            certificate.is_user_uploaded = True
            certificate.assigned_to = request.user
            certificate.save()

            # SHA256 hash
            file_obj = request.FILES['file']
            file_content = file_obj.read()
            certificate.file_hash = hashlib.sha256(file_content).hexdigest()

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            verification_url = f"http://127.0.0.1:8080/verify/{certificate.file_hash}/"
            qr.add_data(verification_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            certificate.qr_code.save(f"{certificate.name}_qr.png", File(buffer), save=False)
            certificate.save()

            message = "✅ Certificate uploaded successfully!"
            return redirect('users:dashboard')
    else:
        form = UserCertificateUploadForm()

    # Only fetch the latest certificate uploaded by this user
    latest_certificate = Certificate.objects.filter(uploaded_by_user=request.user).order_by('-created_at').first()

    return render(request, "user_upload_certificate.html", {
        'form': form,
        'certificate': latest_certificate,
        'message': message,
    })
# User logout
# -------------------------
@login_required(login_url='users_login')
def users_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
    
def add_certificate_to_blockchain(cert_id):
    cert = Certificate.objects.get(id=cert_id)
    # Your blockchain logic: generate QR, hash, store on blockchain
    return True  # or some status

@login_required(login_url='users_login')
def view_certificate(request, pk):
    """
    Allow a user to view a certificate only if it belongs to them.
    """
    cert = get_object_or_404(Certificate, pk=pk, user=request.user)
    return render(request, 'user_portal/view_certificate.html', {'cert': cert})


@login_required(login_url='users_login')
def blockchain_certificates(request):
    certificates = []
    try:
        total = contract.functions.counter().call()  # total certificates on blockchain
        for i in range(1, total + 1):
            doc = contract.functions.getDocument(i).call()
            # Only show certificates belonging to this user
            if doc[2].lower() == request.user.email.lower():  # assuming owner stored as email
                certificates.append({
                    "id": i,
                    "file_hash": doc[0],
                    "timestamp": doc[1],
                    "owner": doc[2],
                })
    except Exception as e:
        print("Error fetching blockchain data:", e)

    message = None
    if not certificates:
        message = "No certificates recorded on blockchain yet."

    return render(request, "users/blockchain_certificates.html", {
        "certificates": certificates,
        "message": message
    })