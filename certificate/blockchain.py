from certificate.models import Certificate
from web3 import Web3
import os
import json
from django.conf import settings

def get_blockchain_connection():
    """Connect to blockchain and return w3 and contract instances"""
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    CONTRACT_ADDRESS = "0x2c61d671Dd1DbD60eB57672491E898f79Bf64ff0"
    contract_path = os.path.join(settings.BASE_DIR, "blockchain", "contracts", "DocumentVerification.json")

    with open(contract_path) as f:
        contract_json = json.load(f)

    contract_data = contract_json["contracts"]["DocumentVerification.sol"]["DocumentVerification"]
    ABI = contract_data["abi"]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    return w3, contract

# -------------------------
# Blockchain helper functions
# -------------------------
def user_certificates(cert_id):
    cert = Certificate.objects.get(id=cert_id)
    print(f"Processing certificate {cert_id} on blockchain")
    return True

def verify_certificate(cert_id):
    w3, contract = get_blockchain_connection()
    try:
        return contract.functions.verifyCertificate(cert_id).call()
    except Exception as e:
        print("Error verifying certificate:", e)
        return False

def add_certificate_to_blockchain(cert_id):
    cert = Certificate.objects.get(id=cert_id)
    w3, contract = get_blockchain_connection()
    # Your blockchain logic to add the certificate
    print(f"Adding certificate {cert_id} to blockchain")
    return True