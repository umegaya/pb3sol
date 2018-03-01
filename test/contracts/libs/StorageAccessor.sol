pragma solidity ^0.4.17;

import "./Restrictable.sol";
import "./Storage.sol";

contract StorageAccessor is Restrictable {
    uint internal constant LOAD_CHUNK_SIZE = 256; //should match with Storage.LOAD_CHUNK_SIZE
    Storage public storageContract; //Storage contract

    function StorageAccessor(address storageAddress) Restrictable() public {
        storageContract = Storage(storageAddress);
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