// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import {ERC20} from "solmate/tokens/ERC20.sol";

// Solmate ERC20 doesn't revert on funds sent to address(0)
contract MocksETH4 is ERC20 {
    constructor() ERC20("SOLMATE", "SLT", 6) {}
}
