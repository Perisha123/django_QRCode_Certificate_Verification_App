from certificate.blockchain import add_certificate_to_blockchain

def store_and_verify_certificate(cert):
    """
    Add a certificate to blockchain and update `is_verified` flag.
    """
    try:
        success = add_certificate_to_blockchain(cert.id)
        if success:
            cert.is_verified = True
            cert.save(update_fields=['is_verified'])
            return True
    except Exception as e:
        print(f"❌ Blockchain error for certificate {cert.id}: {e}")
    return False