from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import qrcode

from users.blockchain_utils import push_certificates_to_blockchain
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
from certificate.blockchain import verify_certificate, add_certificate

# Import Certificate model and form
from certificate.models import Certificate
from certificate.forms import CertificateForm
from users.forms import UserCertificateUploadForm
from .blockchain_utils import push_certificates_to_blockchain
from .blockchain_setup import contract, w3

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
CONTRACT_ADDRESS = "0xB732c3a83Ef1Fcb9865E6D0f3B9fea0bc9371B70"  # Replace with your deployed contract

contract_path = os.path.join(
    settings.BASE_DIR,
    "blockchain",
    "contracts",
    "DocumentVerification.json"
)

with open(contract_path) as f:
    ABI = json.load(f)  # ✅ Your JSON is already ABI

# -----------------------------
# Load contract instance
# -----------------------------
CONTRACT_ADDRESS = "0x184a20380803992726C45c8c43b2bBA075d3F31c"

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

print("✅ Contract loaded successfully!")
# -----------------------------
# View blockchain certificates
# -----------------------------
from django.shortcuts import render
from .blockchain_setup import contract
from qrverify.settings import CONTRACT_ABI, CONTRACT_ADDRESS


@login_required(login_url='users_login')
def view_certificates_blockchain(request):
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    certificates = Certificate.objects.filter(
        uploaded_by_user=request.user
    ) | Certificate.objects.filter(
        assigned_to=request.user
    )
    certificates = certificates.distinct()    
    blockchain_data = []

    for cert in certificates:
        try:
            doc = contract.functions.getDocument(cert.id).call()
            print("🔹 Blockchain doc:", doc)
            blockchain_hash = doc[0]
            timestamp = doc[1]
            verified = (blockchain_hash == cert.file_hash)

        except Exception as e:
            print(f"⚠ Blockchain fetch error for cert {cert.id}: {e}")

            blockchain_hash = None
            timestamp = None
            verified = False

        blockchain_data.append({
            "name": cert.name,
            "hash": cert.file_hash,
            "verified": "✅" if verified else "❌",
            "timestamp": timestamp if 'timestamp' in locals() else None

        })
        message = None
    if not blockchain_data:
        message = "No certificates recorded on blockchain yet."


    context = {"certificates": blockchain_data}
    return render(request, "users/blockchain_certificates.html", context)

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
    # Fetch all certificates uploaded by or assigned to this user
    user_certificates = Certificate.objects.filter(
        Q(uploaded_by_user=request.user) | Q(assigned_to=request.user)
    ).order_by('-created_at')

    # Debugging: see what is fetched
    print(f"DEBUG - Certificates for user {request.user.id} ({request.user.email}): {user_certificates}")

    # Prepare template context
    certs_with_status = []
    for cert in user_certificates:
        certs_with_status.append({
            'cert': cert,
            'source': "You" if cert.uploaded_by_user_id == request.user.id else "Admin Assigned",
            'blockchain_status': "Recorded on Blockchain" if cert.file_hash else "Not recorded"
        })

    if not certs_with_status:
        print("DEBUG - No certificates to show for this user!")

    return render(request, 'users_dashboard.html', {
        'certs_with_status': certs_with_status
    })

# Upload certificate
# -------------------------
from .blockchain_setup import contract 
@login_required(login_url='users_login')
def user_upload_certificate(request):
    message = None
    certificate = None

    if request.method == "POST":
        form = UserCertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.uploaded_by_user = request.user
            certificate.is_user_uploaded = True
            certificate.assigned_to = request.user
            certificate.save()

            # SHA256 hash
            file_obj = request.FILES['file']
            file_content = file_obj.read()
            certificate.file_hash = hashlib.sha256(file_content).hexdigest()
            certificate.save()

            # ✅ ADD THIS BLOCKCHAIN CODE 👇
            try:
                tx = contract.functions.storeCertificate(
                    certificate.id,
                    certificate.file_hash
                ).transact({'from': w3.eth.accounts[0]})

                w3.eth.wait_for_transaction_receipt(tx)
                print("Stored on blockchain ✅")

            except Exception as e:
                print("Blockchain error:", e)

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

    latest_certificate = Certificate.objects.filter(
        uploaded_by_user=request.user
    ).order_by('-created_at').first()

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
    
def add_certificate(cert_id, cert_file_hash):
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
            file_hash = doc[0]
            timestamp = doc[1]
            owner_address = doc[2]

            # Optionally, check if this blockchain certificate exists in Django
            cert_qs = Certificate.objects.filter(file_hash=file_hash, assigned_to=request.user)
            if cert_qs.exists():
                certificates.append({
                    "id": i,
                    "file_hash": file_hash,
                    "timestamp": timestamp,
                    "owner": owner_address,  # display Ethereum address
                    "name": cert_qs.first().name
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