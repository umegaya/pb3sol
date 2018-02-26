var Storage = artifacts.require("./libs/Storage.sol");
var Version1 = artifacts.require("./Version1.sol");
var Version2 = artifacts.require("./Version2.sol");

module.exports = function(deployer) {
  deployer.deploy(Storage).then(function() {
    return deployer.deploy(Version1, Storage.address);
  }).then(function () {
    return deployer.deploy(Version2, Storage.address);
  });
};
