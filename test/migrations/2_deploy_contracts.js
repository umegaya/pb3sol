var Storage = artifacts.require("Storage");
var PbRuntime = artifacts.require("_pb");
var PbCodec = artifacts.require("pb");
//var RewardsCodec2 = artifacts.require("test2_RewardsCodec");
var Version1 = artifacts.require("Version1");
var Version2 = artifacts.require("Version2");

module.exports = function(deployer) {
  deployer.deploy(Storage).then(function() {
    return deployer.deploy(PbRuntime)
  }).then(function () {
    return deployer.deploy(PbCodec);
  })/*.then(function () {
    RewardsCodec2.link(PbRuntime.address);
    return deployer.deploy(RewardsCodec2);
  })//*/.then(function () {
    Version1.link(PbCodec);
    Version1.link(PbRuntime);
    return deployer.deploy(Version1, Storage.address);
  }).then(function () {
    Version2.link(PbCodec);
    Version2.link(PbRuntime);
    return deployer.deploy(Version2, Storage.address);
  })//*/;
};
