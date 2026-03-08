# django_QRCode_Certificate_Verification_App# Blockchain-Based QR Code Verification System

## Project Overview
This project is a **Blockchain-Based QR Code Verification System** developed as part of the **Master of Software Engineering – Industry-Based Capstone Research Project (MSE907)**.  
It provides a **secure, lightweight, and privacy-compliant system** for verifying digital documents using **SHA-256 hashing, QR codes, and a local blockchain**.  

The system addresses issues with traditional centralized verification systems such as tampering, lack of transparency, and high costs of public blockchain networks.

---

## Features
- **Document Verification:** Upload documents and generate SHA-256 hashes for integrity verification.  
- **QR Code Integration:** Generate and scan QR codes linked to blockchain transactions for quick verification.  
- **Blockchain Storage:** Hashes of documents are stored on a local blockchain using Solidity smart contracts and Ganache.  
- **Privacy-Compliant:** Sensitive document data remains off-chain, ensuring compliance with GDPR and NZ Privacy Act 2020.  
- **Modular Architecture:** Frontend, backend, and blockchain layers are separated for easier maintenance and scalability.  

---

## Technologies Used
- **Backend:** Python, Django, Django REST Framework  
- **Blockchain:** Solidity, Web3.py, Ganache (local Ethereum blockchain)  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Database:** MySQL (off-chain storage)  
- **Version Control:** Git & GitHub  
- **Testing:** PyTest (unit testing), Selenium (integration testing)  

---

## System Architecture
The system follows a **three-layer architecture**:

1. **Frontend Layer:** User interface for uploading documents, scanning QR codes, and viewing verification results.  
2. **Backend Layer:** Django REST APIs handle document processing, hash generation, and smart contract communication.  
3. **Blockchain Layer:** Ganache stores only the cryptographic hashes of documents for immutability and verification.

![System Architecture](docs/system_architecture.png)  
*Figure: System architecture diagram (replace with your actual diagram if available)*

---

## Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/Perisha123/django_QRCode_Certificate_Verification_App.git
cd django_QRCode_Certificate_Verification_App