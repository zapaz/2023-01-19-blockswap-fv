import "inc/SyndicateGlobal.spec"

methods {
    isActive(bytes32)     returns (bool)  envfree
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
 * Given one user, for any other random user making whatever calls,
 * their combined sETH amount stays less than total
 */
invariant sETHSolvencyCorrollaryInvariant(address user, address random, bytes32 knot)
    random != user => sETHStakedBalanceForKnot(knot,user) +
                      sETHStakedBalanceForKnot(knot,random) <= sETHTotalStakeForKnot(knot)
    filtered { f -> notHarnessCall(f) }
    {
        preserved with(env e) {
            require e.msg.sender == random;
        }
    }

/**
* On stake, sETH transfered from user to contract
*/
rule onStake() {
    env e; bytes32 key; uint256 amount; address behalf;

    address staker  = e.msg.sender;
    require  staker != currentContract;

    mathint stakerBalBefore    = sETHToken.balanceOf(staker);
    mathint syndicateBalBefore = sETHToken.balanceOf(currentContract);

    stake(e, key, amount, behalf);

    mathint stakerBalAfter    = sETHToken.balanceOf(staker);
    mathint syndicateBalAfter = sETHToken.balanceOf(currentContract);

    assert stakerBalAfter    == stakerBalBefore    - amount;
    assert syndicateBalAfter == syndicateBalBefore + amount;
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
