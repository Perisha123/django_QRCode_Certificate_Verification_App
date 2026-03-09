import os
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Contract address (your deployed contract)
CONTRACT_ADDRESS = "0x980bBAD5bfA4Dd5b09BF40CFBf704ECdD07Cd5D6"

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load contract ABI
with open(os.path.join(BASE_DIR, 'blockchain', 'contracts', 'DocumentVerification.json')) as f:
    contract_json = json.load(f)
    contract_abi = contract_json['contracts']['DocumentVerification.sol']['DocumentVerification']['abi']

# Initialize contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# Home view
def home(request):
    return render(request, "home.html")
# Upload certificate
def upload_certificate(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('certificate_file')
        if not uploaded_file:
            return HttpResponse("No file uploaded!")

        # Save uploaded file locally
        save_dir = os.path.join(BASE_DIR, 'uploaded_files')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded_file.name)

        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Compute file hash (SHA256) for blockchain
        import hashlib
        uploaded_file.seek(0)  # rewind file pointer
        file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()

        # Send transaction to blockchain (register document)
        tx_hash = contract.functions.registerDocument(file_hash).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx_hash)

        return HttpResponse(f"File uploaded and registered successfully! Hash: {file_hash}")

    return render(request, 'upload.html')

# Success view (optional)
def success(request):
    return HttpResponse("Success!")

    from django.http import JsonResponse

def get_counter(request):
    return JsonResponse({"counter": 1})