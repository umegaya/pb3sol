pragma solidity ^0.4.17;

import "./libs/StorageAccessor.sol";
import "./libs/pb/TaskList_pb.sol";

contract Version1 is StorageAccessor {
    //instance method style
    using pb_Rewards for pb_Rewards.Data;
    pb_Rewards.Data public tmp;
    
	function Version1(address storageAddress) StorageAccessor(storageAddress) public {
    }

    function addReward(string key) public writer returns (uint256) {
        pb_Rewards.Data memory r;
        r.id = new uint256[](2);
        r.id[0] = 123;
        r.id[1] = 456;
        r.f1 = 111;
        r.f2 = 222;
        r.f3 = new int64[](2);
        r.f3[0] = 333;
        r.f3[1] = 444;
        saveBytesByString(key, r.encode());
        return r.id[0];
    }

    function loadReward(string key) public writer {
        bytes memory b = loadBytesByString(key);
        tmp.decode(b);
    }//*/

    function getId(uint idx) public view reader returns (uint256) {
        return tmp.id[idx];
    }
    function getF3(uint idx) public view reader returns (int64) {
        return tmp.f3[idx];
    }
    function getF1() public view reader returns (uint64) {
        return tmp.f1;
    }
    function getF2() public view reader returns (uint32) {
        return tmp.f2;
    }//*/
}
