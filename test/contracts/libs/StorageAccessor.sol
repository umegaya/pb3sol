pragma solidity ^0.4.17;

import "./Restrictable.sol";
import "./Storage.sol";
import "./Console.sol";

contract StorageAccessor is Restrictable, Console {
    uint internal constant LOAD_CHUNK_SIZE = 256; //should match with Storage.LOAD_CHUNK_SIZE
    Storage public storageContract; //Storage contract

    function StorageAccessor(address storageAddress) Restrictable() public {
        //log("ctor executed with", msg.sender);
        storageContract = Storage(storageAddress);
        //set writer permission to storage. 
        //thus, deployer should be owner of storageAddress
        /*if (Storage(storageContract).administrator() == msg.sender) {
            log("ctor executed with admin", msg.sender);
        } else {
            log("ctor not executed with admin", msg.sender);
        }
        Storage(storageContract).addWriter(this);*/
    }

    function saveBytesByString(string key, bytes memory b) internal {
        storageContract.setBytesByString(key, b);
    }
    function saveBytesByInt64(int64 key, bytes memory b) internal {
        storageContract.setBytesByInt64(key, b);        
    }
    //after ABIEncoderV2 gets default, 
    //these codes will become just proxy for Storage(storageContract).getBytes(key)
    function loadBytesByString(string key) internal view reader returns (bytes) {
        uint length = storageContract.getBytesLengthByString(key);
        uint offset = 0;
        bytes memory ret = new bytes(length);
        for (;length > offset; offset += LOAD_CHUNK_SIZE) {
            var (chunk, clen) = storageContract.getRangeBytesByString(key, offset);
            for (uint i = 0; i < clen; i++) {
                ret[offset + i] = chunk[i];
            }
        }
        return ret; 
    }
    function loadBytesByInt64(int64 key) internal view reader returns (bytes) {
        uint length = storageContract.getBytesLengthByInt64(key);
        uint offset = 0;
        bytes memory ret = new bytes(length);
        for (;length > offset; offset += LOAD_CHUNK_SIZE) {
            var (chunk, clen) = storageContract.getRangeBytesByInt64(key, offset);
            for (uint i = 0; i < clen; i++) {
                ret[offset + i] = chunk[i];
            }
        }
        return ret;
    }
}
//*/