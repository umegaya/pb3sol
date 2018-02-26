pragma solidity ^0.4.17;

import "./Restrictable.sol";
import "./Storage.sol";
import "./Console.sol";

contract StorageAccessor is Restrictable, Console {
    uint internal constant LOAD_CHUNK_SIZE = 256; //should match with Storage.LOAD_CHUNK_SIZE
    address public storageContract; //Storage contract

    function StorageAccessor(address storageAddress) public {
        //log("ctor executed with", msg.sender);
        storageContract = storageAddress;
        //set writer permission to storage. 
        //thus, deployer should be owner of storageAddress
        /*if (Storage(storageContract).administrator() == msg.sender) {
            log("ctor executed with admin", msg.sender);
        } else {
            log("ctor not executed with admin", msg.sender);
        }
        Storage(storageContract).addWriter(this);*/
    }

    function saveBytes(string key, bytes memory b) internal {
        Storage(storageContract).setBytes(key, b);
    }
    function saveBytes(int64 key, bytes memory b) internal {
        Storage(storageContract).setBytes(key, b);        
    }
    //after ABIEncoderV2 gets default, 
    //these codes will become just proxy for Storage(storageContract).getBytes(key)
    function loadBytes(string key) internal view reader returns (bytes) {
        var s = Storage(storageContract);
        uint length = s.getBytesLength(key);
        uint offset = 0;
        bytes memory ret = new bytes(length);
        for (;length > offset; offset += LOAD_CHUNK_SIZE) {
            var (chunk, clen) = s.getBytes(key, offset);
            for (uint i = 0; i < clen; i++) {
                ret[offset + i] = chunk[i];
            }
        }
        return ret;
    }
    function loadBytes(int64 key) internal view reader returns (bytes) {
        var s = Storage(storageContract);
        uint length = s.getBytesLength(key);
        uint offset = 0;
        bytes memory ret = new bytes(length);
        for (;length > offset; offset += LOAD_CHUNK_SIZE) {
            var (chunk, clen) = s.getBytes(key, offset);
            for (uint i = 0; i < clen; i++) {
                ret[offset + i] = chunk[i];
            }
        }
        return ret;
    }
}
//*/