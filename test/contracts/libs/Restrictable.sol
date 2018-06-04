pragma solidity ^0.4.17;

contract Restrictable {
    enum Privilege { None, Read, Write }
    address public administrator;
    mapping (address => Privilege) public members;

    constructor() public {
        administrator = msg.sender;
    }

    modifier admin {
        require(msg.sender == administrator);
        _;
    }

    modifier writer {
        require(msg.sender == administrator || uint(members[msg.sender]) >= uint(Privilege.Write));
        _;
    }

    modifier reader {
        require(msg.sender == administrator || uint(members[msg.sender]) >= uint(Privilege.Read));
        _;
    }

    function changeOwner(address newAdmin) public admin {
        if (newAdmin != address(0)) {
            administrator = newAdmin;
        }
    }

    function setPrivilege(address member, Privilege p) public writer {
        if (uint(p) <= uint(Privilege.Write)) {
            members[member] = p;
        }
    }
}
