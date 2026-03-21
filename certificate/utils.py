# certificate/utils.py
from users.blockchain_setup import w3, contract

def store_and_verify_certificate(certificate):
    try:
        cert_hash = certificate.file_hash
        tx_hash = contract.functions.storeCertificateHash(cert_hash).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            certificate.is_verified = True
            certificate.save(update_fields=['is_verified'])
            return True
        else:
            return False
    except Exception as e:
        print("Blockchain recording failed:", e)
        return False