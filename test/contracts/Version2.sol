pragma solidity ^0.4.17;

import "./libs/StorageAccessor.sol";
import "./libs/pb/TaskList2_pb.sol";

contract Version2 is StorageAccessor {
    pb.Rewards public tmp;

	function Version2(address storageAddress) StorageAccessor(storageAddress) public {
    }

    function addReward(string key) public writer {
        pb.Rewards memory r;
        r.f1 = 111;
        r.f2 = 222;
        r.f3 = new int64[](2);
        r.f3[0] = 333;
        r.f3[1] = 444;
        r.new_id = 123456;
        saveBytesByString(key, pb.encodeRewards(r));
    }

    function loadReward(string key) public writer {
        bytes memory b = loadBytesByString(key);
        tmp = pb.decodeRewards(b);
        if (tmp.new_id == 0) {
            tmp.new_id = tmp.id[0];
            saveBytesByString(key, pb.encodeRewards(tmp));
        }
    }

    function loadRewardLen(string key) public view reader returns (uint256) {
        bytes memory b = loadBytesByString(key);
        return b.length;
    }

    function getId(uint idx) public view reader returns (uint256) {
        return tmp.id[idx];
    }
    function getNewId() public view reader returns (uint256) {
        return tmp.new_id;
    }
    function getF3(uint idx) public view reader returns (int64) {
        return tmp.f3[idx];
    }
    function getF1() public view reader returns (uint64) {
        return tmp.f1;
    }
    function getF2() public view reader returns (uint32) {
        return tmp.f2;
    } //*/
}
