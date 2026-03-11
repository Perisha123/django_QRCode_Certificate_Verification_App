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
import json
from django.utils.crypto import get_random_string
from qrcode.constants import ERROR_CORRECT_H
from web3 import Web3
from django.conf import settings

# Import Certificate model and form
from certificate.models import Certificate
from certificate.forms import CertificateForm

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

# -----------------------------
# Blockchain interaction helpers
# -----------------------------
def add_certificate(cert_id):
    """Add certificate ID to blockchain"""
    try:
        tx = contract.functions.addCertificate(cert_id).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx)
        return True
    except Exception as e:
        print("Error adding certificate to blockchain:", e)
        return False

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
@login_required
def users_dashboard(request):
    certificates = Certificate.objects.filter(user=request.user)

    # Verify blockchain status for each certificate
    certs_with_status = []
    for cert in certificates:
        # Push to blockchain if not already recorded
        if not verify_certificate(cert.id):
            add_certificate(cert.id)

        blockchain_status = verify_certificate(cert.id)
        certs_with_status.append({
            'cert': cert,
            'blockchain_status': blockchain_status
        })

    return render(request, "users_dashboard.html", {
        'certificates': certs_with_status
    })

# -------------------------
# Upload certificate
# -------------------------
@login_required
def upload_certificate(request):
    # Initialize variable to avoid UnboundLocalError
    blockchain_status = None

    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.user = request.user
            certificate.save()

            # Example: simulate blockchain addition
            blockchain_status = "Certificate successfully added to blockchain!"
        else:
            blockchain_status = "Failed to upload certificate. Please check the form."
    else:
        form = CertificateForm()

    return render(request, "user_upload_certificate.html", {
        'form': form,
        'blockchain_status': blockchain_status,
    })
   
# -------------------------
# User logout
# -------------------------
@login_required(login_url='users_login')
def users_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
    