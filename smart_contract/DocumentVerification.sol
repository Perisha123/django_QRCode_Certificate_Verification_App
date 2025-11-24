// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerification {

    struct Record {
        string fileHash;      // SHA-256 hash of document
        uint256 timestamp;    // time stored
        address owner;        // who uploaded
    }

    mapping(uint256 => Record) public records;
    uint256 public counter;

    // Store document hash
    function storeHash(string memory hashValue) public returns(uint256) {
        counter++;
        records[counter] = Record({
            fileHash: hashValue,
            timestamp: block.timestamp,
            owner: msg.sender
        });
        return counter;
    }

    // Get hash by ID
    function getHash(uint256 id) public view returns(string memory) {
        require(id > 0 && id <= counter, "Invalid ID");
        return records[id].fileHash;
    }

    // Get timestamp
    function getTimestamp(uint256 id) public view returns(uint256) {
        require(id > 0 && id <= counter, "Invalid ID");
        return records[id].timestamp;
    }

    // Get owner of record
    function getOwner(uint256 id) public view returns(address) {
        require(id > 0 && id <= counter, "Invalid ID");
        return records[id].owner;
    }
}
