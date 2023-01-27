import "inc/SyndicateGlobal.spec"

methods {
    isActive        (bytes32)           returns (bool)      envfree
    sETHBalanceOf   (bytes32, address)  returns (uint256)   envfree
}

/**
 * Address 0 must have zero sETH balance.
 */
invariant addressZeroHasNoBalance()
    sETHToken.balanceOf(0) == 0
    filtered { f -> notHarnessCall(f) }

/**
 * TotalStake is 12 ether max
 */
invariant maxTotalStake()
    sETHToken.totalSupply() <= 12000000000000000000
    filtered { f -> notHarnessCall(f) }

/**
 * Sum of two balances is allways less than Total :
 * Given one user, for any other random user making whatever calls,
 * their combined sETH balances stays less than Total
 */
invariant sETHSolvencyCorrollary(address user, address random, bytes32 knot)
    random != user => sETHStakedBalanceForKnot(knot, user) +
                      sETHStakedBalanceForKnot(knot, random) <= sETHTotalStakeForKnot(knot)
    filtered { f -> notHarnessCall(f) }
    {
        preserved with(env e) {
            require e.msg.sender == random;
        }
    }

/**
* On stake, sETH amount is transfered from user to contract
*/
rule stakeRule() {
    env e; bytes32 key; uint256 amount; address behalf;

    address staker  = e.msg.sender;
    require  staker != currentContract;

    mathint stakerBalBefore    = sETHBalanceOf(key, staker);
    mathint syndicateBalBefore = sETHBalanceOf(key, currentContract);

    stake(e, key, amount, behalf);

    mathint stakerBalAfter     = sETHBalanceOf(key, staker);
    mathint syndicateBalAfter  = sETHBalanceOf(key, currentContract);

    assert stakerBalAfter    == stakerBalBefore    - amount;
    assert syndicateBalAfter == syndicateBalBefore + amount;
}

/**
* On unstake, sETH amount is transfered from user to contract
*/
rule unstakeRule() {
    env e; bytes32 key; uint256 amount;
    address ethTo;
    address unstaker;
    require unstaker != currentContract;

    mathint sethToBalBefore    = sETHBalanceOf(key, unstaker);
    mathint syndicateBalBefore = sETHBalanceOf(key, currentContract);

    unstake(e, ethTo, unstaker, key, amount);

    mathint sethToBalAfter    = sETHBalanceOf(key, unstaker);
    mathint syndicateBalAfter = sETHBalanceOf(key, currentContract);

    assert syndicateBalAfter == syndicateBalBefore - amount;
    assert sethToBalAfter    == sethToBalBefore    + amount;
}

/**
* AccumulatedETH or totalClaimed allways increase
*/
rule alwaysIncrease(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;

    mathint amount1Before = accumulatedETHPerFreeFloatingShare();
    mathint amount2Before = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3Before = totalClaimed();

    f(e, args);

    mathint amount1After  = accumulatedETHPerFreeFloatingShare();
    mathint amount2After  = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3After  = totalClaimed();

    assert amount1After  >= amount1Before;
    assert amount2After  >= amount2Before;
    assert amount3After  >= amount3Before;
}

/**
 * An unregistered knot can not be deregistered.
 */
rule canNotDegisterUnregisteredKnot(method f) filtered {
    f -> notHarnessCall(f)
} {
    bytes32 knot; env e;
    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}


/**
 * Total ETH received must not decrease.
 */
rule totalEthReceivedMonotonicallyIncreases(method f) filtered {
    f -> notHarnessCall(f)
}{

    uint256 totalEthReceivedBefore = totalETHReceived();

    env e; calldataarg args;
    f(e, args);

    uint256 totalEthReceivedAfter = totalETHReceived();

    assert totalEthReceivedAfter >= totalEthReceivedBefore, "total ether received must not decrease";
}

