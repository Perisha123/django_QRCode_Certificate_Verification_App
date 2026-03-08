// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DocumentVerification {

    struct Record {
        string fileHash;
        uint256 timestamp;
        address owner;
    }

    mapping(uint256 => Record) public records;
    uint256 public counter;

    // Store document hash on blockchain
    function storeDocument(string memory _hash) public returns (uint256) {
        counter++;

        records[counter] = Record(
            _hash,
            block.timestamp,
            msg.sender
        );

        return counter;
    }

    // Retrieve stored hash
    function getDocument(uint256 _id) public view returns (
        string memory,
        uint256,
        address
    ) {
        Record memory r = records[_id];
        return (r.fileHash, r.timestamp, r.owner);
    }

    // Verify hash
    function verifyDocument(uint256 _id, string memory _hash)
        public view returns (bool)
    {
        Record memory r = records[_id];

        return keccak256(bytes(r.fileHash))
        == keccak256(bytes(_hash));
    }
}