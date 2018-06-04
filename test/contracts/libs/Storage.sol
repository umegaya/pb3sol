pragma solidity ^0.4.17;

import "./Restrictable.sol";

contract Storage is Restrictable {
    uint public constant LOAD_CHUNK_SIZE = 256;
    mapping (string => bytes) stringMap;

    constructor() Restrictable() public {
    }

    function getBytesByString(string key) public view reader returns (bytes) {
        return stringMap[key];
    }
    function getRangeBytesByString(string key, uint offset) public view reader returns (byte[256], uint) {
        bytes memory bs = stringMap[key];
        byte[256] memory rbs;
        uint remain = bs.length - offset;
        if (remain < 0) {
            return (rbs, 0);
        } else if (remain > 256) {
            remain = offset + 256;
        } else {
            remain = bs.length;
        }
        for (uint i = offset; i < remain; i++) {
            rbs[i - offset] = bs[i];
        }
        return (rbs, remain);
    }
    function getBytesLengthByString(string key) public view reader returns (uint) {
        bytes memory bs = stringMap[key];
        return bs.length;        
    }
    function setBytesByString(string key, bytes data) public writer returns (bool) {
        bytes memory prev = stringMap[key];
        stringMap[key] = data;
        assert(stringMap[key].length > 0);
        return prev.length > 0;
    }
}
