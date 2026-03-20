# users/blockchain_utils.py
from certificate.models import Certificate
from .blockchain_setup import contract, w3

def push_certificates_to_blockchain():
    for i, cert in enumerate(Certificate.objects.all()):
        try:
            # Check if this index already exists on blockchain
            if i < contract.functions.counter().call():
                blockchain_file_hash, _, _ = contract.functions.getDocument(i).call()
                if blockchain_file_hash == cert.file_hash:
                    print(f"{cert.name} already on blockchain ✅")
                    continue

            # Push certificate to blockchain
            tx_hash = contract.functions.addcertificate(cert.file_hash).transact({
                'from': w3.eth.accounts[0]
            })
            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"{cert.name} added to blockchain 🔹 tx: {tx_hash.hex()}")

        except Exception as e:
            print(f"Error pushing {cert.name}: {e}")

    print("✅ All certificates processed")