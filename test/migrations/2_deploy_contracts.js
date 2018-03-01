var Storage = artifacts.require("Storage");
var PbRuntime = artifacts.require("_pb");
var RewardsCodec = artifacts.require("pb_Rewards");
var RewardsCodec2 = artifacts.require("pb2_Rewards");
var Version1 = artifacts.require("Version1");
var Version2 = artifacts.require("Version2");

module.exports = function(deployer) {
  deployer.deploy(Storage).then(function() {
    return deployer.deploy(PbRuntime)
  }).then(function () {
    RewardsCodec.link(PbRuntime);
    return deployer.deploy(RewardsCodec);
  }).then(function () {
    RewardsCodec2.link(PbRuntime);
    return deployer.deploy(RewardsCodec2);
  }).then(function () {
    Version1.link(RewardsCodec);
    return deployer.deploy(Version1, Storage.address);
  }).then(function () {
    Version2.link(RewardsCodec2);
    return deployer.deploy(Version2, Storage.address);
  })//*/;
};
