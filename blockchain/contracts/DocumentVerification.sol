// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerification {
    struct Document {
        string fileHash;
        uint timestamp;
        address owner;
    }

    Document[] public documents;

    function addcertificate(string memory fileHash) public {
        documents.push(Document(fileHash, block.timestamp, msg.sender));
    }

    function verifycertificate(uint index) public view returns (bool) {
        return index < documents.length;
    }

    function getDocument(uint index) public view returns (string memory, uint, address) {
        Document storage doc = documents[index];
        return (doc.fileHash, doc.timestamp, doc.owner);
    }

    function counter() public view returns (uint) {
        return documents.length;
    }
}