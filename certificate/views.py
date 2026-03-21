import email
import hashlib
from unittest import result
import qrcode
import os
from openpyxl import Workbook
# from .blockchain import contract  # type: ignore
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
from django.contrib.auth.models import User
from django.http import FileResponse
from django.http import HttpResponse
from .blockchain import verify_certificate as blockchain_verify
from certificate.models import Certificate
# at the top of certificate/views.py
from .forms import CertificateForm
from .blockchain import  verify_certificate, add_certificate, get_blockchain_connection
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
    certificates = Certificate.objects.filter(
        is_user_uploaded=False  # only admin certificates
    ).order_by('-created_at')

    query = request.GET.get('q')  # get search input
    if query:
        certificates = certificates.filter(
            Q(name__icontains=query) | Q(user__email__icontains=query)
        )

    total = certificates.count()

    return render(request, 'admin_dashboard.html', {
        'certificates': certificates,
        'total': total,
        'query': query  # keep search input in form
    })



from users.blockchain_setup import contract, w3  # your Web3 + contract
def record_certificate_on_chain(certificate):
    try:
        cert_hash = certificate.hash
        tx_hash = contract.functions.storeCertificateHash(cert_hash).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        certificate.is_verified = True
        certificate.save()
    except Exception as e:
        print("Blockchain recording failed:", e)


# --------------------------------------------------
# UPLOAD CERTIFICATE (User + Blockchain)@login_required(login_url='users_login')
def upload_certificate(request):
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)

        if form.is_valid():
            file_obj = request.FILES.get('file')
            
            # ✅ Check if file is uploaded
            if not file_obj:
                messages.error(request, "No file uploaded.")
                return redirect('upload_certificate')

            # ✅ Validate PDF
            if not file_obj.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed!")
                return redirect('upload_certificate')

            if file_obj.content_type != 'application/pdf':
                messages.error(request, "Uploaded file is not a valid PDF.")
                return redirect('upload_certificate')

            # ✅ Check empty file
            file_data = file_obj.read()
            if not file_data:
                messages.error(request, "Uploaded file is empty.")
                return redirect('upload_certificate')

            file_obj.seek(0)  # reset pointer for saving

            # ✅ Generate file hash
            hash_value = hashlib.sha256(file_data).hexdigest()

            # --- Get the actual user by email ---
            user_email = form.cleaned_data.get('email')
            assigned_user = User.objects.filter(email=user_email).first()  # None if not registered

            # --- Create certificate ---
            certificate = Certificate.objects.create(
                name=form.cleaned_data['name'],
                email=assigned_user.email if assigned_user else form.cleaned_data['email'],
                file=file_obj,
                uploaded_by_user=request.user,
                is_user_uploaded=False,
                assigned_to=assigned_user,
                file_hash=hash_value
            )

            # --- Generate QR code ---
            qr_url = f"{request.scheme}://{request.get_host()}/verify/{hash_value}/"
            qr = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT_H, box_size=10, border=4)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            filename = f"{hash_value}_{get_random_string(4)}.png"
            certificate.qr_code.save(filename, ContentFile(buffer.getvalue()))
            certificate.save()
            buffer.close()

            # --- Blockchain ---
            from certificate.utils import store_and_verify_certificate
            store_and_verify_certificate(certificate)
            try:
                success = add_certificate(certificate.id, certificate.file_hash)
                if success:
                    certificate.is_verified = True
                    certificate.save(update_fields=['is_verified'])
                    messages.success(request, "Certificate uploaded and recorded on blockchain successfully!")
                else:
                    messages.warning(request, "Certificate uploaded, but blockchain recording failed.")
            except Exception as e:
                messages.warning(request, f"Blockchain error: {e}")

            if not assigned_user:
                messages.warning(request, f"No registered user with email '{user_email}'. Certificate unassigned.")

            return redirect('admin_dashboard')
    else:
        form = CertificateForm()

    return render(request, 'upload_certificate.html', {'form': form})
# --------------------------------------------------
# USER DASHBOARD
from django.db.models import Q
@login_required(login_url='users_login')
def users_dashboard(request):
    certificates = Certificate.objects.filter(
        Q(assigned_to=request.user) | Q(uploaded_by_user=request.user)
    )

    for cert in certificates:
        try:
            cert.is_verified = verify_certificate(cert.id, cert.file_hash)
            cert.save(update_fields=['is_verified'])
        except Exception as e:
            print(f"ERROR verifying cert {cert.id}: {e}")
            cert.is_verified = False

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
# User: View Certificate
# ------------------------
@login_required(login_url='users_login')
def verify_certificate(request, cert_id):
    """
    Display certificate and verify its hash on the blockchain.
    """
    certificate = get_object_or_404(Certificate, id=cert_id)
    verified = False

    try:
        # Connect to blockchain
        w3, contract = get_blockchain_connection()

        # Call verifyCertificate (read-only)
        verified = contract.functions.verifyCertificate(cert_id, certificate.file_hash).call()

    except Exception as e:
        messages.warning(request, f"Blockchain verification failed: {e}")

    return render(request, "user_portal/verify_certificate.html", {
        'certificate': certificate,
        'verified': verified
    })

from .blockchain import get_blockchain_connection

def user_upload_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.uploaded_by_user = True
            cert.assigned_to = request.user

            # Compute SHA256 hash of uploaded file
            uploaded_file = request.FILES['file']  # make sure your form field is 'file'
            file_content = uploaded_file.read()
            hash_value = hashlib.sha256(file_content).hexdigest()
            cert.sha256_hash = hash_value

            cert.save()
            from certificate.utils import store_and_verify_certificate
            store_and_verify_certificate(cert)

            # Blockchain transaction
            try:
                w3, contract = get_blockchain_connection()
                tx_hash = contract.functions.storeCertificate(
                    cert.id,
                    cert.sha256_hash
                ).transact({'from': w3.eth.accounts[0]})
                w3.eth.wait_for_transaction_receipt(tx_hash)
                messages.success(request, "Certificate uploaded and recorded on blockchain!")
            except Exception as e:
                messages.warning(request, f"Certificate uploaded, but blockchain recording failed: {e}")

            return redirect('users_dashboard')
        else:
            messages.error(request, "Form is invalid. Please check the fields and try again.")
    else:
        form = CertificateForm()

    return render(request, 'user_upload_certificate.html', {'form': form})


@login_required(login_url='users_login')
def certificate_download(request, cert_id):
    # Ensure user can only download their own user-uploaded certificates
    cert = get_object_or_404(Certificate, id=cert_id)

    # If you want, you can restrict downloads:
    # if cert.uploaded_by_user and cert.uploaded_by != request.user:
    #     return HttpResponse("You are not allowed to download this certificate.")

    file_path = cert.certificate_file.path  # adjust field name if needed

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse("File not found.")
    

@login_required
def export_certificates_excel(request):
    certificates = Certificate.objects.all()
    
    # Create a new workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Certificates"
    
    # Header row
    ws.append(['ID', 'User Email', 'Certificate Name', 'Hash', 'Created At'])
    
    # Data rows
    for cert in certificates:
        ws.append([cert.id, cert.email, cert.name, cert.file_hash, cert.created_at.strftime('%Y-%m-%d %H:%M')])
    
    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=certificates.xlsx'
    wb.save(response)
    return response


def view_certificates_html(request):
    # Fetch all certificates
    certificates = Certificate.objects.all()
    return render(request, 'certificates_table.html', {'certificates': certificates})

def verify_certificate_on_blockchain(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)

    # send certificate to blockchain
    tx = contract.functions.addCertificate(certificate.id, certificate.file_hash).transact({'from': w3.eth.accounts[0]})
    receipt = w3.eth.wait_for_transaction_receipt(tx)

    # update the certificate
    certificate.is_verified = True
    certificate.blockchain_tx_hash = receipt.transactionHash.hex()  # must be a real DB field!
    certificate.save(update_fields=['is_verified', 'blockchain_tx_hash'])

    return redirect('certificate_detail', certificate_id=certificate.id)
