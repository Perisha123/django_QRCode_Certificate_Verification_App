from web3 import Web3
from django.conf import settings
from certificate.models import Certificate
from pathlib import Path
import json

# --------------------------
# Connect to Ganache & load contract
# --------------------------
def get_blockchain_connection():
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Replace if your RPC differs
    if not w3.is_connected():
        raise ConnectionError("❌ Ganache is not connected!")

    # Load contract ABI from JSON
    contract_path = Path(settings.BASE_DIR) / 'blockchain' / 'contracts' / 'DocumentVerification.json'
    with open(contract_path) as f:
     contract_json = json.load(f)

    # Extract ABI
    try:
        abi = contract_json['contracts']['DocumentVerification.sol']['DocumentVerification']['abi']
    except KeyError:
        raise KeyError("❌ ABI not found in JSON. Check your compiled contract structure.")

    # Get deployed contract address from settings
    contract_address = getattr(settings, 'CONTRACT_ADDRESS', None)
    if not contract_address:
        raise ValueError("❌ CONTRACT_ADDRESS not set in settings.py")

    contract = w3.eth.contract(address=contract_address, abi=abi)

    return w3, contract

# --------------------------
# Store certificate on blockchain
# --------------------------
def add_certificate_to_blockchain(cert_id):
    try:
        cert = Certificate.objects.get(id=cert_id)
    except Certificate.DoesNotExist:
        print(f"❌ Certificate with ID {cert_id} does not exist.")
        return False

    w3, contract = get_blockchain_connection()

    try:
        tx_hash = contract.functions.storeDocument(cert.file_hash).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Certificate {cert.id} stored on blockchain!")
        return True
    except Exception as e:
        print(f"❌ Failed to store certificate {cert.id}: {e}")
        return False

# --------------------------
# Verify certificate on blockchain
# --------------------------
def verify_certificate(cert_id):
    try:
        cert = Certificate.objects.get(id=cert_id)
    except Certificate.DoesNotExist:
        print(f"❌ Certificate with ID {cert_id} does not exist.")
        return False

    w3, contract = get_blockchain_connection()

    try:
        verified = contract.functions.verifyDocument(cert.id, cert.file_hash).call()
        print(f"✅ Verification result for certificate {cert.id}: {verified}")
        return verified
    except Exception as e:
        print(f"❌ Error verifying certificate {cert.id}: {e}")
        return False

# --------------------------
# Get certificate details from blockchain (optional)
# --------------------------
def get_certificate_from_blockchain(cert_id):
    w3, contract = get_blockchain_connection()
    try:
        file_hash, timestamp, owner = contract.functions.getDocument(cert_id).call()
        return {
            "file_hash": file_hash,
            "timestamp": timestamp,
            "owner": owner
        }
    except Exception as e:
        print(f"❌ Error fetching certificate {cert_id}: {e}")
        return None