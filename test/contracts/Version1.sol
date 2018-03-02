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
        //id array
        r.id = new uint256[](2);
        r.id[0] = 123;
        r.id[1] = 456;
        
        //fixed64
        r.f1 = 111;

        //array of message which contains array of message
        r.f2 = new pb_TaskList_Task.Data[](2);

        r.f2[0].due_date = 20180303;
        r.f2[0].progresses = new pb_TaskList_Task_Progress.Data[](2);
        r.f2[0].progresses[0].step = 1;
        r.f2[0].progresses[1].step = -111;

        r.f2[1].due_date = 20180401;
        r.f2[1].progresses = new pb_TaskList_Task_Progress.Data[](1);
        r.f2[1].progresses[0].step = 3;

        //int64 array
        r.f3 = new int64[](2);
        r.f3[0] = 333;
        r.f3[1] = 444;

        //int128 with negative value
        r.f4 = -3;

        saveBytesByString(key, r.encode());
        return r.id[0];
    }

    function loadReward(string key) public writer {
        bytes memory b = loadBytesByString(key);
        tmp.decode(b);
    }//*/

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
        return 0;
    }
}
