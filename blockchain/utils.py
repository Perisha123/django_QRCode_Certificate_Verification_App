from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Load ABI and contract address
with open("blockchain/contract_data.json") as f:
    data = json.load(f)

contract_address = data["address"]
abi = data["abi"]

contract = w3.eth.contract(address=contract_address, abi=abi)

def add_certificate(cert_id):
    tx = contract.functions.addCertificate(cert_id).transact({'from': w3.eth.accounts[0]})
    w3.eth.wait_for_transaction_receipt(tx)
    return True

def verify_certificate(cert_id):
    return contract.functions.verifyCertificate(cert_id).call()