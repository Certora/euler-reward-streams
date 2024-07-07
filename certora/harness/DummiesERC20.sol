// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "openzeppelin-contracts/token/ERC20/ERC20.sol";


/// @title Am implementation of ERC20
contract DummyERC20A is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
    }
}


/// @title Am implementation of ERC20
contract DummyERC20B is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
    }
}


/// @title Am implementation of ERC20
contract DummyERC20C is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
    }
}


/// @title Am implementation of ERC20
contract DummyERC20D is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {
    }
}
