from web3 import Web3
import json
import os

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Check connection
if not w3.is_connected():
    raise Exception("❌ Ganache not connected!")

# Set default account (first Ganache account)
w3.eth.default_account = w3.eth.accounts[0]

# Load compiled contract JSON (Remix format)
json_path = os.path.join(os.path.dirname(__file__), "contracts/DocumentVerification.json")
with open(json_path) as f:
    contract_json = json.load(f)

# Get ABI and bytecode
abi = contract_json['abi']
bytecode = contract_json['bytecode']

# Create contract instance
DocumentVerification = w3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy contract
tx_hash = DocumentVerification.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("✅ Contract deployed!")
print("Contract Address:", tx_receipt.contractAddress)