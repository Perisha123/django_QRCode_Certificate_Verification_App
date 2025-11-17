// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerification {
    struct Record {
        string fileHash;
        uint256 timestamp;
    }

    mapping(uint256 => Record) public records;
    uint256 public counter;

    function storeHash(string memory hashValue) public returns(uint256) {
        counter++;
        records[counter] = Record(hashValue, block.timestamp);
        return counter;
    }

    function getHash(uint256 id) public view returns(string memory) {
        return records[id].fileHash;
    }
}
