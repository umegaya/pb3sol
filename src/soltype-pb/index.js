var Bigint = require('big-integer');
var MaxUint128Plus1 = Bigint("100000000000000000000000000000000", 16);
var MaxUint256Plus1 = Bigint("10000000000000000000000000000000000000000000000000000000000000000", 16);

function hexdump(arr) {
    var hex = "0123456789ABCDEF";
    return arr.map(b => hex[(0xF0 & b) >> 4] + hex[0x0F & b]);
}
var SolidityPrototypeExtension = {
    isAddress: function() {
        return this.type == "address";
    },
    toAddress: function () {
        return "0x" + hexdump(this.data);
    },
    isNumber: function() {
        return this.type == "int" || this.type == "uint";
    },
    toNumber: function () {
        var ret = 0;
        for (var i = 0; i < this.data.length; i++) {
            var b = Number(this.data[i]);
            ret = (ret << 8) + b;
        }
        if (Number(this.data[0]) >= 0x80 && this.type == "int") {
            maxuint = (1 << (this.data.length * 8));
            ret = ret - maxuint;
        }
        return ret;
    },
    isBigint: function () {
        return this.type == "bigint" || this.type == "biguint";
    },
    toBigint: function () {
        if (this.type == "biguint") {
            return Bigint.fromArray(this.data, 256);
        } else {
            var val = Bigint.fromArray(this.data, 256);
            var tmp = this.data[0];
            if (tmp > 0x80) {
                switch (this.data.length) {
                case 16:
                    return val.subtract(MaxUint128Plus1);
                case 32:
                    return val.subtract(MaxUint256Plus1);
                default:
                    throw new Error("invalid array length:" + this.data.length);
                }
            } else {
                return val;
            }
        }
    },
    isBytes: function() {
        return this.type == "bytes";
    },
    toBytes: function () {
        return this.data;
    }
}
function Soliditize(proto, typename) {
    function SolidityType(properties) {
        this.type = typename;
    }
    Object.assign(SolidityType.prototype, SolidityPrototypeExtension);
    proto.ctor = SolidityType;
}
module.exports = {
    importTypes: function (proto) {
        Soliditize(proto.lookup("solidity.address"), "address");
        [8, 16].forEach(function (v) {
            Soliditize(proto.lookup("solidity.uint" + v.toString()), "uint");
            Soliditize(proto.lookup("solidity.int" + v.toString()), "int");
        });
        ["", 128, 256].forEach(function (v) {
            Soliditize(proto.lookup("solidity.uint" + v.toString()), "biguint");
            Soliditize(proto.lookup("solidity.int" + v.toString()), "bigint");
        });
        for (var i = 1; i <= 32; i++) {
            Soliditize(proto.lookup("solidity.bytes" + i), "bytes");
        }//*/
    },
    importProtoFile: function (protobufjs) {
        var origResolvePath = protobufjs.Root.prototype.resolvePath;
        protobufjs.Root.prototype.resolvePath = function (filename, path) {
            if (path.endsWith("Solidity.proto")) {
                return origResolvePath(filename, __dirname + "/include/Solidity.proto");
            }
            return origResolvePath(filename, path);
        }
        return protobufjs;
    },
}
