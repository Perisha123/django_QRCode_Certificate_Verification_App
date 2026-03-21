// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerification {
    struct Document {
        string fileHash;
        uint timestamp;
        address owner;
    }

    Document[] public documents;
    mapping(string => bool) public hashExists;
    mapping(uint => Document) public documentsById;

function addCertificate(uint certId, string memory fileHash) public {
    documentsById[certId] = Document(fileHash, block.timestamp, msg.sender);
}

function verifyCertificate(uint certId, string memory fileHash) public view returns (bool) {
    Document memory doc = documentsById[certId];
    return (keccak256(bytes(doc.fileHash)) == keccak256(bytes(fileHash)));
}

function getDocument(uint certId) public view returns (string memory, uint, address) {
    Document memory doc = documentsById[certId];
    return (doc.fileHash, doc.timestamp, doc.owner);
}

function counter() public view returns (uint) {
        return documents.length;
    }
}