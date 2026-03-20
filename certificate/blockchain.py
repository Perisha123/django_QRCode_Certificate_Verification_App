import os
import json
from web3 import Web3
from django.conf import settings
from certificate.models import Certificate

# -------------------------
# Blockchain connection
# -------------------------
def get_blockchain_connection():
    """Connect to blockchain and return w3 and contract instances"""
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

    # Check connection
    if w3.is_connected():
        print("✅ Connected to Ganache!")
    else:
        print("❌ Blockchain connection failed")

    # Contract address
    CONTRACT_ADDRESS = "0xDC2A8e12C90eBf6DD54f51772B451E53159649b7"

    # Load ABI
    contract_path = os.path.join(settings.BASE_DIR, "blockchain", "contracts", "DocumentVerification.json")
    with open(contract_path) as f:
        contract_json = json.load(f)

    contract_data = contract_json["contracts"]["DocumentVerification.sol"]["DocumentVerification"]
    ABI = contract_data["abi"]

    # Load contract
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    print("✅ Contract loaded successfully")

    return w3, contract

# -------------------------
# Blockchain helper functions
# -------------------------
def add_certificate_to_blockchain(cert_id):
    cert = Certificate.objects.get(id=cert_id)
    w3, contract = get_blockchain_connection()

    # Generate SHA256 hash for file
    file = cert.file
    import hashlib
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    file_hash = hasher.hexdigest()

    try:
        tx_hash = contract.functions.storeCertificate(cert_id, file_hash).transact({
            'from': w3.eth.accounts[0]
        })
        print(f"✅ Certificate {cert_id} stored on blockchain: {tx_hash}")
        return True
    except Exception as e:
        print(f"❌ Failed to store certificate {cert_id} on blockchain:", e)
        return False

def verify_certificate(cert_id):
    w3, contract = get_blockchain_connection()
    try:
        blockchain_hash = contract.functions.getCertificate(cert_id).call()
        print(f"Blockchain hash for certificate {cert_id}: {blockchain_hash}")
        return blockchain_hash
    except Exception as e:
        print("❌ Error verifying certificate:", e)
        return False