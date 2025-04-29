// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AccessControl {
    string private storedHash;
    mapping(address => bool) public authorized;

    function registerFile(string memory ipfsHash) public {
        storedHash = ipfsHash;
    }

    function grantAccess(address user) public {
        authorized[user] = true;
    }

    function accessFile() public view returns (string memory) {
        require(authorized[msg.sender], "Access denied");
        return storedHash;
    }
}
