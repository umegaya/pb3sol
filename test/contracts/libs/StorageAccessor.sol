pragma solidity ^0.4.24;

import "./Restrictable.sol";
import "./Storage.sol";

contract StorageAccessor is Restrictable {
    uint internal constant LOAD_CHUNK_SIZE = 256; //should match with Storage.LOAD_CHUNK_SIZE
    Storage public storageContract; //Storage contract

    constructor(address storageAddress) Restrictable() public {
        storageContract = Storage(storageAddress);
    }

    function saveBytesByString(string key, bytes memory b) internal {
        storageContract.setBytesByString(key, b);
    }
    //after ABIEncoderV2 gets default, 
    //these codes will become just proxy for Storage(storageContract).getBytes(key)
    function loadBytesByString(string key) internal view reader returns (bytes) {
        return Storage(storageContract).getBytesByString(key);
    }
}
//*/