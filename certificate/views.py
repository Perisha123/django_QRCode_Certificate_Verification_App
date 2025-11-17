from django.shortcuts import render
from django.conf import settings
from web3 import Web3
import hashlib
import qrcode
import os

# Connect to Ganache blockchain
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Load smart contract
contract = web3.eth.contract(
    address=settings.CONTRACT_ADDRESS,
    abi=settings.CONTRACT_ABI
)

# Make sure static/qr exists
QR_FOLDER = os.path.join("static", "qr")
os.makedirs(QR_FOLDER, exist_ok=True)


def upload_document(request):
    if request.method == "POST":
        uploaded_file = request.FILES["document"]
        file_bytes = uploaded_file.read()

        # 1. Create SHA-256 hash
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # 2. Store hash on blockchain
        tx = contract.functions.storeHash(file_hash).transact({
            "from": web3.eth.accounts[0]
        })
        web3.eth.wait_for_transaction_receipt(tx)

        # 3. Get new record ID
        record_id = contract.functions.counter().call()

        # 4. Generate QR Code (contains record ID)
        qr_path = os.path.join(QR_FOLDER, f"{record_id}.png")
        qr = qrcode.make(str(record_id))
        qr.save(qr_path)

        return render(request, "success.html", {
            "record_id": record_id,
            "qr_path": f"/static/qr/{record_id}.png"
        })

    return render(request, "upload.html")


def verify_document(request):
    if request.method == "POST":
        record_id = int(request.POST["record_id"])
        uploaded_file = request.FILES["document"]
        new_hash = hashlib.sha256(uploaded_file.read()).hexdigest()

        stored_hash = contract.functions.getHash(record_id).call()

        status = "Authentic Document" if new_hash == stored_hash else "Tampered Document"

        return render(request, "result.html", {"status": status})

    return render(request, "verify.html")
