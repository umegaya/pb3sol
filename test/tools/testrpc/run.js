var ganache = require("ganache-core");
var server = ganache.server({
    host: "localhost", 
    network_id:4447,
    mnemonic: "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat",
    gasLimit: 67219750,
    logger: console,
});
server.listen(9545, function(err, blockchain) {
});
