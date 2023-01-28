// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SyndicateHarnessOrig} from "./SyndicateHarnessOrig.sol";

contract SyndicateHarness is SyndicateHarnessOrig {
    mapping(bytes32 => address) sETHTokens;

    function getSETH(blsKey key) public view returns (IERC20 sETH) {
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(key));
        sETH = IERC20(getSlotRegistry().stakeHouseShareTokens(stakeHouse));
    }

    function sETHBalanceOf(blsKey key, address addr) public view returns (uint256) {
        return getSETH(key).balanceOf(addr);
    }

    function sETHTotalSupply(blsKey key) public view returns (uint256) {
        return getSETH(key).totalSupply();
    }

    function isActive(blsKey key) public view returns (bool active) {
        (,,,,, active) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(key));
    }

    function calculateCollateralizedETHOwedPerKnot() public view returns (uint256) {
        return _calculateCollateralizedETHOwedPerKnot();
    }

    function calculateNewAccumulatedETHPerCollateralizedShare(uint256 lastEthAmount) public view returns (uint256) {
        return _calculateNewAccumulatedETHPerCollateralizedShare(lastEthAmount);
    }
}
