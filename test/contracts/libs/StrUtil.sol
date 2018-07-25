pragma solidity ^0.4.17;

library StrUtil {
	function Compare(string a, string b) internal pure returns (bool) {
		return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b));
	}
}
