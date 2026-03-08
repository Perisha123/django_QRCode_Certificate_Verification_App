from web3 import Web3
import json

# Ganache local blockchain URL
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Set default account (first Ganache account)
w3.eth.default_account = w3.eth.accounts[0]

# Load compiled smart contract JSON
with open("smart_contract/DocumentVerification.json") as f:
    contract_json = json.load(f)

abi = contract_json["abi"]
bytecode = contract_json["bytecode"]

# Deploy contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = contract.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Save contract address + ABI to JSON for backend
contract_data = {
    "address": tx_receipt.contractAddress,
    "abi": abi
}

with open("backend/blockchain/contract_address.json", "w") as f:
    json.dump(contract_data, f, indent=4)

print("Contract deployed successfully!")
print("Contract Address:", tx_receipt.contractAddress)