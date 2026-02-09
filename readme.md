# Getting Started With the QR code Certificate Verification Web App

## Cloning Our Repository into Our Local Machine
To get started with using and testing the project on our local machine, we have to clone the remote repository onto our local repostory, We can get this done by copy and pasting this code to our terminal:

```
git clone https://github.com/mqnifestkelvin/django_QRCode_Certificate_Verification_App.git
```

**Note**: If you don't have git installed on your local machine follow the direction below according to the platform you currently make use of
   * For windows, click [here](https://git-scm.com/download/win) to install and get started and start using git. Also for those who are new to using git here is a useful [video](https://www.simplilearn.com/tutorials/git-tutorial/git-installation-on-windows) on how to get started using git for cloning on windows.
   
   # Blockchain-Based QR Code Verification System

## Overview
This project is a **lightweight, privacy-conscious blockchain-based document verification system** designed for small institutions such as schools, training centers, and certification authorities.  

It combines **SHA-256 hashing**, a **local Ganache blockchain**, **QR codes**, and a **Django web application** with **Web3.py** integration to provide a fast, secure, and tamper-proof verification process.

---

## Features
- **SHA-256 Hashing:** Each uploaded document is hashed to ensure integrity. Any changes to the document will produce a different hash.  
- **Ganache Local Blockchain:** Stores document hashes permanently in a decentralized manner, eliminating the need for expensive public networks.  
- **QR Code Integration:** Each document is linked to a QR code that points to its blockchain transaction for quick verification.  
- **Django Web Application:** Backend for document upload, hash generation, verification, and user authentication.  
- **Web3.py Integration:** Facilitates communication between Django and smart contracts on the local blockchain.  
- **Privacy-Compliant:** Only cryptographic hashes are stored on-chain to comply with **NZ Privacy Act 2020** and **GDPR**.  
- **Cloud Deployment:** Can be deployed on platforms like AWS or Render for small-scale institutional use.

---

## Project Structure
**django_QRCode_Certificate_Verification_App/**
│
├── certificate/ # Django app for certificate management
├── qrverify/ # Django app for QR code scanning and verification
├── smart_contract/ # Solidity smart contracts
├── manage.py # Django project management file
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── .gitignore # Ignore unnecessary files (venv, pycache, etc.)


---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Perisha123/django_QRCode_Certificate_Verification_App.git
cd django_QRCode_Certificate_Verification_App

2. **Set up a virtual environment**

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux


**Install dependencies**

pip install -r requirements.txt


Run Django server

python manage.py runserver


**Open your browser**
Navigate to http://127.0.0.1:8000 to access the web application.

Smart Contracts

storeDocumentHash() – Stores SHA-256 hashes on the blockchain.

retrieveDocumentHash() – Retrieves a document hash using the QR code transaction ID.

verifyDocument() – Compares the uploaded document hash with the stored hash.

## Usage

Upload a document to the Django application.

SHA-256 hash is generated and stored on the local Ganache blockchain via smart contract.

A QR code is generated linking to the blockchain transaction.

Verifiers scan the QR code and upload the document to verify authenticity.

The system compares hashes and outputs:

Match: Document is authentic

Mismatch: Document has been tampered

Technologies Used

Python 3.x

Django 4.x

Django REST Framework

Solidity (Smart Contracts)

Ganache (Local Blockchain)

Web3.py

SHA-256 Hashing

QR Code generation

Bootstrap, HTML, CSS (Frontend)

Privacy and Security

No personal or sensitive data is stored on-chain.

Compliant with NZ Privacy Act 2020 and GDPR.

Ensures tamper-proof document verification.

QR codes are cryptographically linked to blockchain transactions.