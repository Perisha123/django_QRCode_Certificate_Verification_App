# users/blockchain_setup.py
import os
import json
from web3 import Web3

# -----------------------------
# 1️⃣ Connect to Ganache
# -----------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    raise Exception("⚠️ Cannot connect to Ganache!")

# Set default account
w3.eth.default_account = w3.eth.accounts[0]

# -----------------------------
# 2️⃣ Load ABI
# -----------------------------
json_path = os.path.join(os.path.dirname(__file__), "../blockchain/contracts/DocumentVerification.json")

with open(json_path) as f:
    abi = json.load(f)  # Since your JSON is already a list of function objects

# -----------------------------
# 3️⃣ Contract address
# -----------------------------
contract_address = "0x184a20380803992726C45c8c43b2bBA075d3F31c"  # Replace with your deployed contract address

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

print("✅ Contract loaded successfully")