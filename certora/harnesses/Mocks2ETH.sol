// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import {MocksETH} from "./MocksETH.sol";

// Override MocksETH to get transfer function returning false on failure instead of reverting
contract Mocks2ETH is MocksETH {
    function transfer(address recipient, uint256 amount) public override returns (bool ok) {
        if (ok = balanceOf(_msgSender()) >= amount) super.transfer(recipient, amount);
    }
}
