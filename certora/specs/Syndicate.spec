import "inc/SyndicateGlobal.spec"

/**
 * Address 0 must have zero balance for any StakeHouse sETH
 */
invariant sETHAddressZeroHasNoBalance(bytes32 key)
    sETHBalanceOf(key, 0) == 0
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
    address ethTo; address unstaker;

    require unstaker != currentContract;

    mathint sethToBalBefore    = sETHBalanceOf(key, unstaker);
    mathint syndicateBalBefore = sETHBalanceOf(key, currentContract);

    unstake(e, ethTo, unstaker, key, amount);

    mathint sethToBalAfter     = sETHBalanceOf(key, unstaker);
    mathint syndicateBalAfter  = sETHBalanceOf(key, currentContract);

    assert syndicateBalAfter  == syndicateBalBefore - amount;
    assert sethToBalAfter     == sethToBalBefore    + amount;
}

/**
* Minimum rule derived from unstakeRule to detect bug1
*/
rule bug1Rule() {
    env e; bytes32 key; uint256 amount;
    address ethTo; address unstaker;

    require amount > 0;
    require unstaker != currentContract;

    mathint sethToBalBefore    = sETHBalanceOf(key, unstaker);
    unstake(e, ethTo, unstaker, key, amount);
    mathint sethToBalAfter     = sETHBalanceOf(key, unstaker);

    assert sethToBalAfter != sethToBalBefore;
}

/**
* Vacuous rule to detect bug5
*/
rule bug5Rule(method f) filtered {
   f -> notHarnessCall(f)
}{
    mathint knots        = numberOfRegisteredKnots();
    mathint last         = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint totalETH     = totalETHReceived();
    mathint unprocessed  = getUnprocessedETHForAllCollateralizedSlot();

    require knots       != 0;

    assert unprocessed  ==  ( ( totalETH / 2 ) - last) / knots ;
}

/**
* AccumulatedETH, totalClaimed and totalETHReceived allways increase
*/
rule monotonicallyIncreases(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;

    mathint amount1Before = accumulatedETHPerFreeFloatingShare();
    mathint amount2Before = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3Before = totalClaimed();
    mathint amount4Before = totalETHReceived();
    mathint amount5Before = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount6Before = lastSeenETHPerFreeFloating();

    f(e, args);

    mathint amount1After  = accumulatedETHPerFreeFloatingShare();
    mathint amount2After  = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3After  = totalClaimed();
    mathint amount4After  = totalETHReceived();
    mathint amount5After  = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount6After  = lastSeenETHPerFreeFloating();

    assert amount1After  >= amount1Before;
    assert amount2After  >= amount2Before;
    assert amount3After  >= amount3Before;
    assert amount4After  >= amount4Before;
    assert amount5After  >= amount5Before;
    assert amount6After  >= amount6Before;
}

/**
 * An unregistered knot can not be deregistered.
 */
rule canNotDeregisterUnregisteredKnot(method f) filtered {
    f -> notHarnessCall(f)
} {
    bytes32 knot; env e;
    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}
