import hashlib
import json
import qrcode

from django.shortcuts import render, redirect
from django.conf import settings
from .models import Certificate

from web3 import Web3


# ----------------------------
# Blockchain connection
# ----------------------------

GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

contract_address = "YOUR_CONTRACT_ADDRESS"

abi = [
    {
        "inputs": [{"internalType": "string", "name": "_hash", "type": "string"}],
        "name": "storeDocument",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_id", "type": "uint256"},
            {"internalType": "string", "name": "_hash", "type": "string"},
        ],
        "name": "verifyDocument",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]

contract = w3.eth.contract(address=contract_address, abi=abi)


# ----------------------------
# SHA256 HASH FUNCTION
# ----------------------------

def generate_hash(file):

    sha256 = hashlib.sha256()

    for chunk in file.chunks():
        sha256.update(chunk)

    return sha256.hexdigest()


# ----------------------------
# HOME PAGE
# ----------------------------

def home(request):
    return render(request, "home.html")


# ----------------------------
# UPLOAD CERTIFICATE
# ----------------------------

def upload_certificate(request):

    if request.method == "POST":

        file = request.FILES["file"]

        # Generate hash
        file_hash = generate_hash(file)

        # Save certificate
        cert = Certificate.objects.create(
            file=file,
            file_hash=file_hash
        )

        # Store hash on blockchain
        tx = contract.functions.storeDocument(
            file_hash
        ).transact(
            {"from": w3.eth.accounts[0]}
        )

        receipt = w3.eth.wait_for_transaction_receipt(tx)

        cert.tx_hash = receipt.transactionHash.hex()
        cert.blockchain_id = cert.id
        cert.save()

        # Generate QR
        generate_qr(cert)

        return redirect("success")

    return render(request, "upload.html")


# ----------------------------
# QR CODE GENERATION
# ----------------------------

def generate_qr(cert):

    data = {
        "certificate_id": cert.id,
        "tx_hash": cert.tx_hash,
        "hash": cert.file_hash,
    }

    qr_data = json.dumps(data)

    qr = qrcode.make(qr_data)

    qr_path = f"{settings.MEDIA_ROOT}/qr/cert_{cert.id}.png"

    qr.save(qr_path)


# ----------------------------
# VERIFY CERTIFICATE
# ----------------------------

def verify_certificate(request, cert_id):

    cert = Certificate.objects.get(id=cert_id)

    file = cert.file

    recalculated_hash = generate_hash(file)

    result = contract.functions.verifyDocument(
        cert.blockchain_id,
        recalculated_hash
    ).call()

    if result:
        status = "VALID CERTIFICATE"
    else:
        status = "TAMPERED CERTIFICATE"

    return render(
        request,
        "verify.html",
        {
            "certificate": cert,
            "status": status
        }
    )


# ----------------------------
# SUCCESS PAGE
# ----------------------------

def success(request):

    return render(request, "success.html")