pragma solidity ^0.4.17;

import "./Restrictable.sol";

contract Storage is Restrictable {
    uint public constant LOAD_CHUNK_SIZE = 256;
    mapping (string => bytes) stringMap;
    mapping (int64 => bytes) integerMap;

    function Storage() public {
    }

    function getBytes(string key) public view reader returns (bytes) {
        return stringMap[key];
    }
    function getBytes(string key, uint offset) public view reader returns (byte[256], uint) {
        bytes memory bs = stringMap[key];
        byte[256] memory rbs;
        uint remain = bs.length - offset;
        if (remain < 0) {
            revert();
        }
        for (uint i = offset; i < remain; i++) {
            rbs[i - offset] = bs[i];
        }
        return (rbs, remain);
    }
    function getBytesLength(string key) public view reader returns (uint) {
        bytes memory bs = stringMap[key];
        return bs.length;        
    }

    function getBytes(int64 key) public view reader returns (bytes) {
        return integerMap[key];
    }
    function getBytes(int64 key, uint offset) public view reader returns (byte[256], uint) {
        bytes memory bs = integerMap[key];
        byte[256] memory rbs;
        uint remain = bs.length - offset;
        if (remain < 0) {
            revert();
        }
        for (uint i = offset; i < remain; i++) {
            rbs[i - offset] = bs[i];
        }
        return (rbs, remain);
    }
    function getBytesLength(int64 key) public view reader returns (uint) {
        bytes memory bs = integerMap[key];
        return bs.length;        
    }

    function setBytes(string key, bytes data) public writer returns (bytes) {
        bytes memory prev = stringMap[key];
        stringMap[key] = data;
        return prev;
    }

    function setBytes(int64 key, bytes data) public writer returns (bytes) {
        bytes memory prev = integerMap[key];
        integerMap[key] = data;
        return prev;
    }
}
