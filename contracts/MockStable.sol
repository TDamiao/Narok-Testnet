// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockStable is ERC20 {
    uint8 private immutable _decimals;
    address public owner;

    constructor(string memory name_, string memory symbol_, uint8 decimals_) ERC20(name_, symbol_) {
        _decimals = decimals_;
        owner = msg.sender;
        _mint(msg.sender, 1_000_000 * (10 ** decimals_)); // seed
    }

    function decimals() public view override returns (uint8) { return _decimals; }

    function faucet(address to, uint256 amount) external {
        require(msg.sender == owner, "only owner");
        _mint(to, amount);
    }
}