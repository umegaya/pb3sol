pragma solidity ^0.4.17;

import "truffle/Assert.sol";
import "truffle/DeployedAddresses.sol";
import "../contracts/Version1.sol";

contract TestV1Access {
    Version1 v1 = Version1(DeployedAddresses.Version1());
    // Version2 v2 = Version2(DeployedAddresses.Version2());

    // Testing the adopt() function
    function testAccessRewards_V1_V1() public {
        v1.addReward("reward1");
        v1.loadReward("reward1");
        Assert.equal(v1.getId(0), 123, "err id[0]");
        Assert.equal(v1.getId(1), 456, "err id[1]");
        //uint64 expected_u64 = 111; 
        //Assert.equal(r.f1, expected_u64, "err f1");
        //Assert.equal(r.f2, 222, "err f2");
        Assert.equal(v1.getF3(0), 333, "err f3[0]");
        Assert.equal(v1.getF3(1), 444, "err f3[1]"); 
    }
}
