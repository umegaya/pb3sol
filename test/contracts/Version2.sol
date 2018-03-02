pragma solidity ^0.4.17;

import "./libs/StorageAccessor.sol";
import "./libs/pb/TaskList2_pb.sol";

contract Version2 is StorageAccessor {
    //library method call style
    pb2_Rewards.Data public tmp;

	function Version2(address storageAddress) StorageAccessor(storageAddress) public {
    }

    function addReward(string key) public writer {
        pb2_Rewards.Data memory r;
        r.f1 = 111;
        r.f3 = new int64[](2);
        r.f3[0] = 333;
        r.f3[1] = 444;
        r.new_id = 123456;
        saveBytesByString(key, pb2_Rewards.encode(r));
    }

    function loadReward(string key) public writer {
        bytes memory b = loadBytesByString(key);
        pb2_Rewards.store(pb2_Rewards.decode(b), tmp);
        if (tmp.new_id == 0) {
            tmp.new_id = tmp.id[0];
            saveBytesByString(key, pb2_Rewards.encode(tmp));
        }
    }

    function loadRewardLen(string key) public view reader returns (uint256) {
        bytes memory b = loadBytesByString(key);
        return b.length;
    }

    function check() public view reader returns (int) {
        if (tmp.id[0] != 123) { return -1; }
        if (tmp.id[1] != 456) { return -2; }
        if (tmp.f1 != 111) { return -3; }
        if (tmp.f2[0].due_date != 20180303) { return -4; }
        if (tmp.f2[1].due_date != 20180401) { return -5; }
        if (tmp.f2[0].progresses[0].step != 1) { return -6; }
        if (tmp.f2[0].progresses[1].step != -111) { return -7; }
        if (tmp.f2[1].progresses[0].step != 3) { return -8; }
        if (tmp.f4 != -3) { return -9; }    
        if (tmp.new_id != 123) { return -10; }
        return 0;
    }

    function getNewId() public view reader returns (uint256) {
        return tmp.new_id;
    }
}
