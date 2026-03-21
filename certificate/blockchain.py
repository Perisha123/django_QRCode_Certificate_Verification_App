import os
import json
from web3 import Web3

# -----------------------------
# 1️⃣ Connect to Ganache
# -----------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    raise Exception("❌ Cannot connect to Ganache!")

# Set default account for sending transactions
w3.eth.default_account = w3.eth.accounts[0]

# -----------------------------
# 2️⃣ Load ABI from JSON
# -----------------------------
# BASE_DIR points to project root (where manage.py is)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Correct path to your JSON file
json_path = os.path.join(BASE_DIR, "blockchain", "contracts", "DocumentVerification.json")

with open(json_path) as f:
    abi_list = json.load(f)

# If JSON is a list (Remix export), use first element if needed
if isinstance(abi_list, list) and len(abi_list) == 1 and "abi" in abi_list[0]:
    abi = abi_list[0]["abi"]
else:
    abi = abi_list  # already a list of functions

# -----------------------------
# 3️⃣ Contract address
# -----------------------------
CONTRACT_ADDRESS = "0x70636583A4bfe37eA81b0DEb086137c34b93f421"  # Replace with your deployed contract address

# Create contract object
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# -----------------------------
# 4️⃣ Helper functions
# -----------------------------

def add_certificate(cert_id: int, file_hash: str):
    """Add a certificate to the blockchain"""
    tx = contract.functions.addCertificate(cert_id, file_hash).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    return receipt.transactionHash.hex()


def verify_certificate(cert_id: int, file_hash: str) -> bool:
    """Verify if a certificate exists on blockchain"""
    return contract.functions.verifyCertificate(cert_id, file_hash).call()

def get_blockchain_connection():
    """
    Returns a tuple (web3_instance, contract_instance)
    """
    w3_instance = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3_instance.is_connected():
        raise Exception("Cannot connect to Ganache")

    w3_instance.eth.default_account = w3_instance.eth.accounts[0]

    # Load ABI
    json_path = os.path.join(
        os.path.dirname(__file__), "blockchain", "contracts", "DocumentVerification.json"
    )
    with open(json_path) as f:
        abi_list = json.load(f)
    if isinstance(abi_list, list) and len(abi_list) == 1 and "abi" in abi_list[0]:
        abi = abi_list[0]["abi"]
    else:
        abi = abi_list

    # Contract address (replace with your deployed contract)
    CONTRACT_ADDRESS = "0x70636583A4bfe37eA81b0DEb086137c34b93f421"

    contract_instance = w3_instance.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    return w3_instance, contract_instance


def hash_exists(file_hash: str) -> bool:
    """Check if a file hash already exists"""
    return contract.functions.hashExists(file_hash).call()


def get_document(cert_id: int):
    file_hash, timestamp, owner_address = contract.functions.getDocument(cert_id).call()
    return {
        "file_hash": file_hash,
        "timestamp": timestamp,
        "owner_address": owner_address
    }