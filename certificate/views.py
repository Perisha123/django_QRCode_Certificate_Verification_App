import hashlib
import qrcode
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.crypto import get_random_string
from qrcode.constants import ERROR_CORRECT_H
from django.http import FileResponse
from certificate.blockchain import user_certificates
from django.http import HttpResponse
from users.views import verify_certificate
from certificate.models import Certificate
from .models import Certificate
from .forms import CertificateForm
from certificate.blockchain import user_certificates, verify_certificate, add_certificate_to_blockchain
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

        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, "Welcome Admin!")
            return redirect('admin_dashboard')

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
def admin_dashboard(request):

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

    show_qr = None
    blockchain_status = None
    blockchain_status_class = None
    filename = None

    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)

            # SHA256 hash of uploaded file
            file_obj = request.FILES['file']
            file_data = file_obj.read()
            hash_value = hashlib.sha256(file_data).hexdigest()
            file_obj.seek(0)
            certificate.file_hash = hash_value

            # Uploaded by current user
            certificate.uploaded_by = request.user

            # Assign to selected user
            selected_user = form.cleaned_data.get('assigned_to')
            if selected_user:
                certificate.assigned_to = selected_user

            # Save certificate first (needed for ImageField)
            certificate.save()

            # -----------------------
            # Generate QR code and save directly to ImageField
            # -----------------------
            qr_url = f"{request.scheme}://{request.get_host()}/verify/{hash_value}/"
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save image into Django ImageField
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            random_suffix = get_random_string(6)
            filename = f"{hash_value}_{random_suffix}.png"
            certificate.qr_code.save(filename, ContentFile(buffer.getvalue()))
            certificate.save()
            buffer.close()

            show_qr = certificate.qr_code.url

            # -----------------------
            # Record on Blockchain
            # -----------------------
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

    certificates = Certificate.objects.filter(user=request.user)

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

# ------------------------
# Admin: List Certificates
# ------------------------
def admin_certificates(request):
    certificates = Certificate.objects.all()
    return render(request, 'admin_portal/certificates_list.html', {'certificates': certificates})

# ------------------------
# Admin: Edit Certificate
# ------------------------
def edit_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate updated successfully!")
            return redirect('upload_certificate')
    else:
        form = CertificateForm(instance=cert)
    return render(request, 'admin_portal/edit_certificate.html', {'form': form})

# ------------------------
# Admin: Delete Certificate
# ------------------------
def delete_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    cert.delete()
    messages.success(request, "Certificate deleted successfully!")
    return redirect('admin_dashboard')

# ------------------------
## ------------------------
def verify_certificate_in_blockchain(cert_id):
    """
    Verifies if a certificate exists on the blockchain.
    Returns True if verified, False otherwise.
    """
    try:
        # Example: assuming you have contract and web3 set up
        # Replace these with your actual contract setup
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache or other provider
        contract_address = '0xYourContractAddressHere'
        abi = [...]  # your contract ABI
        contract = w3.eth.contract(address=contract_address, abi=abi)

        return contract.functions.verifyCertificate(cert_id).call()
    except Exception as e:
        print("Blockchain verification error:", e)
        return False
# User: View Certificate
# ------------------------
@login_required(login_url='users_login')
def verify_certificate(request, file_hash):
    certificates = Certificate.objects.filter(file_hash=file_hash, user=request.user)
    certificate = certificates.latest('id')  # returns None if no match

    if not certificate:
        return HttpResponse("Certificate not found or not assigned to you.")

    # Call the helper, not the view itself
    blockchain_status = verify_certificate_in_blockchain(certificate.id)
    return render(request, 'user_portal/verify_certificate.html', {
        'certificate': certificate,
        'blockchain_status': blockchain_status
    })
def user_upload_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate uploaded successfully!")
            return redirect('home')
    else:
        form = CertificateForm()

    return render(request, 'user_upload_certificate.html', {'form': form})

def certificate_download(request, cert_id):
    cert = get_object_or_404(Certificate, id=cert_id)

    file_path = cert.certificate_file.path  # change if your field name is different

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)