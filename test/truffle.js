module.exports = {
  networks: {
    development: {
      //assume user uses ganache ethereum client with default setting
      host: "localhost",
      port: 9545, 
      network_id: "*", // Match any network id
      gas: 4e6,
		  gasPrice: 2e10
    }
  }
};
