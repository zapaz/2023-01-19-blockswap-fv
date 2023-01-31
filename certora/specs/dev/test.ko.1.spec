import "../Syndicate.spec"

methods {
    sETHTotalSupply (bytes32)           returns (uint256)   envfree
}

/**
 * TotalStake of any StakeHouse sETH is 12 ether max
 */
invariant sETHMaxTotalSupply(bytes32 key)
    sETHTotalSupply(key) <= 12000000000000000000
    filtered { f -> notHarnessCall(f) }

/**
 * NOT WORKING => TotalStake of any StakeHouse sETH should be above 11 ether max
 */
invariant sETHMaxTotalSupply(bytes32 key)
    sETHTotalSupply(key) <= 11000000000000000000
    filtered { f -> notHarnessCall(f) }
