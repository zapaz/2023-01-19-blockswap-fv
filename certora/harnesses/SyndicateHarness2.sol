// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SyndicateHarness} from "./SyndicateHarness.sol";

contract SyndicateHarness2 is SyndicateHarness {
    function sETHBalanceOf(blsKey input, address addr) public view returns (uint256) {
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(input));
        IERC20 sETH = IERC20(getSlotRegistry().stakeHouseShareTokens(stakeHouse));

        return sETH.balanceOf(addr);
    }

    function isActive(blsKey input) public view returns (bool active) {
        (,,,,, active) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(input));
    }
}
