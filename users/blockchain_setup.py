# users/blockchain_setup.py
import os
import json
from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    print("⚠️ Ganache not running")
    exit()

# Load contract JSON
json_path = os.path.join(os.path.dirname(__file__), "../blockchain/contracts/DocumentVerification.json")
with open(json_path) as f:
    contract_json = json.load(f)

# Get ABI from nested structure
abi = contract_json["contracts"]["DocumentVerification.sol"]["DocumentVerification"]["abi"]

# Set your deployed contract address here
contract_address = "0x41BBEb73046660cb0747d4e5F355Cd3710044fF9"

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

print("✅ Contract loaded successfully")




