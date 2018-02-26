pragma solidity ^0.4.17;

contract Restrictable {
    address public administrator;
    mapping (address => bool) public writers;
    mapping (address => bool) public readers;

    function Restrictable() public {
        administrator = msg.sender;
    }

    modifier admin {
        require(msg.sender == administrator);
        _;
    }

    modifier writer {
        require(msg.sender == administrator || writers[msg.sender] == true);
        _;
    }

    modifier reader {
        require(msg.sender == administrator || writers[msg.sender] == true || readers[msg.sender] == true);
        _;
    }

    function changeOwner(address newAdmin) public admin {
        if (newAdmin != address(0)) {
            administrator = newAdmin;
        }
    }

    function addWriter(address newWriter) public writer {
        if (writers[newWriter] == false) {
            writers[newWriter] = true;
        }
    }

    function removeWriter(address oldWriter) public writer {
        if (writers[oldWriter] == true) {
            writers[oldWriter] = false;
        }
    }

    function addReader(address newReader) public writer {
        if (readers[newReader] == false) {
            readers[newReader] = true;
        }
    }

    function removeReader(address oldReader) public writer {
        if (readers[oldReader] == true) {
            readers[oldReader] = false;
        }
    }
}
