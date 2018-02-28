var Version1 = artifacts.require('Version1');
var Storage = artifacts.require('Storage');

contract('Storage', function(accounts) {
    it("can deploy Storage contract", function() {
        var c, log;
        return Storage.deployed().then(function(instance) {
            c = instance;
            return c.setBytesByString("key1", "pb3");
        }).then(function(ret) {
            return c.getBytesLengthByString.call("key1");
        }).then(function(ret) {
            var len = ret.toNumber();
            assert.equal(len, 3, "should return 3");
            return c.getRangeBytesByString.call("key1", 0);
        }).then(function(ret) {
            var len = ret[1].toNumber();
            assert.equal(len, 3, "should return 3 bytes array");
            assert.equal(ret[0].slice(0, len).map(b => String.fromCharCode(b)).join(''), "pb3", 
                "should return bytes 'pb3' as text");
        });
    });
});
contract('Version1', function(accounts) {
    it("should put/get pb.Rewards", function() {
        var c;
        return Version1.deployed(Storage.address).then(function(instance) {
            c = instance;
            return c.addReward("reward1");
        }).then(function() {
            return c.loadReward("reward1");
        }).then(function(ret) {
            return c.getId.call(0);
        }).then(function(ret) {
            assert.equal(ret.toNumber(), 123, "id[0] should return 123");
            return c.getF3.call(1);
        }).then(function(ret) {
            assert.equal(ret.toNumber(), 444, "f3[1] should return 444");
        });
    });
});
