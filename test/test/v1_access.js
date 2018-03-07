var Version1 = artifacts.require('Version1');
var Version2 = artifacts.require('Version2');
var Storage = artifacts.require('Storage');

var soltype = require(__dirname + "/../../src/soltype-pb");
var protobuf = soltype.importProtoFile(require("protobufjs")); //import Solidity.proto to default path

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
contract('Versions', function(accounts) {
    it("should put/get pb.Rewards even if schema changes", function() {
        var c, sc;
        var proto;
        //first create bytes object with version1 schema
        return Version1.deployed(Storage.address).then(function(instance) {
            c = instance;
            return c.addReward("reward1");
        }).then(function (ret) {
            assert(false, "should not success without write privilege");
        }, function (err) {
            console.log("recover failure by giving write privilege to", Version1.address.toString());
            return Storage.deployed().then(function(storage_instance) {
                sc = storage_instance;
                return storage_instance.setPrivilege(Version1.address, 2);
            });
        }).then(function(ret) {
            return c.addReward("reward1");
        }).then(function(ret) {
            return c.loadReward("reward1");
        }).then(function(ret) {
            return c.check.call();
        //test interoperability with protobufjs
        }).then(function (ret) {
            assert.equal(ret.toNumber(), 0, "check fails with (" + ret.toNumber() + ")");
            return new Promise(function (resolve, reject) {
                protobuf.load("proto/TaskList.proto", function(err, proto) {
                    if (err) { reject(err); }
                    else { 
                        soltype.importTypes(proto); //add solidity type definition
                        resolve(proto); 
                    }
                });
            });
        }).then(function (ret) {
            proto = ret;
            return sc.getRangeBytesByString.call("reward1", 0);
        }).then(function(ret) {
            /*console.log('bytes');
            var hex = "0123456789ABCDEF";
            for (var i = 0; i < ret[1]; i++) {
                var code = ret[0][i];
                var h = hex[(0xF0 & code) >> 4] + hex[0x0F & code];
                console.log(h)
            } */
            var RewardsProto = proto.lookup("Rewards");
            //this slice will not need after solidity 0.4.21 
            //because dynamic length array can be used for return value of function afterward.
            var rewards = RewardsProto.decode(ret[0].slice(0, ret[1]));
            console.log(rewards);
            assert.equal(rewards.id[0].isBigint() && rewards.id[1].isBigint(), true, "id array type should correct");
            assert.equal(rewards.id[0].toBigint().toString(), "123", "id[0] should correct");
            assert.equal(rewards.id[1].toBigint().toString(), "456", "id[1] should correct");
            assert.equal(rewards.f1, 111, "f1 should correct");
            assert.equal(rewards.f2[0].dueDate, 20180303, "f2[0].due_date should correct");
            assert.equal(rewards.f2[0].progresses[0].step.isNumber() && rewards.f2[0].progresses[1].step.isNumber(), 
                        true, "f2[0] progress type should correct");
            assert.equal(rewards.f2[0].progresses[0].step.toNumber(), 1, "f2[0].progresses[0].step should correct");
            assert.equal(rewards.f2[0].progresses[1].step.toNumber(), -111, "f2[0].progresses[1].step should correct");
            assert.equal(rewards.f4.toBigint().toString(), "-3", "f4 should correct");

        //then, load it with version2 schema (with convert)
            var c2;
            return Version2.deployed(Storage.address).then(function(instance) {
                c2 = instance;
                return Storage.deployed().then(function(storage_instance) {
                    return storage_instance.setPrivilege(Version2.address, 2);
                });
            }).then(function () {
                return c2.loadReward("reward1");
            }).then(function () {
                return c2.check.call();
            }).then(function (ret) {
                assert.equal(ret.toNumber(), 0, "check fails with (" + ret.toNumber() + ")");
                return c2.addReward("reward2");
            }).then(function () {
                return c2.loadReward("reward2");
            }).then(function () {
                return c2.getNewId.call();
            }).then(function (ret) {
                assert.equal(ret.toNumber(), 123456, "brand new new_id should return 123456");
            });
        });
    });
});
