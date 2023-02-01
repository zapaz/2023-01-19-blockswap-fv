import "inc/SyndicateGlobal.spec"

/**
* Divide by Zero Bug
*
* getUnprocessedETHForAllCollateralizedSlot() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot1(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    getUnprocessedETHForAllCollateralizedSlot@withrevert();

    assert !lastReverted , "getUnprocessedETHForAllCollateralizedSlot should not revert with zero registered knots";
}

/**
* Divide by Zero Bug
*
* previewUnclaimedETHAsCollateralizedSlotOwner() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot2(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    previewUnclaimedETHAsCollateralizedSlotOwner@withrevert(args);

    assert !lastReverted , "previewUnclaimedETHAsCollateralizedSlotOwner should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateNewAccumulatedETHPerCollateralizedShare() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot3(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateNewAccumulatedETHPerCollateralizedShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerCollateralizedShare should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateCollateralizedETHOwedPerKnot() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot4(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateCollateralizedETHOwedPerKnot@withrevert(args);

    assert !lastReverted , "calculateCollateralizedETHOwedPerKnot should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateNewAccumulatedETHPerFreeFloatingShare() reverts with zero floating share
*/
rule zeroDivOnZeroFloatingShare(calldataarg args){
    require totalFreeFloatingShares() == 0;

    calculateNewAccumulatedETHPerFreeFloatingShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerFreeFloatingShare should not revert with zero floating share";
}


/**
* Check that after unstaking, sETH amount is transfered from contract to user
*/
rule stakingUnstake() {
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

rule stakingClaim() {
    env e; bytes32 k; address addr;

    requireInvariant knotsSyndicatedCount();
    requireInvariant numberOfRegisteredKnotsInvariant();
    requireInvariant lastAccumulatedIsNoLongerSyndicated(k);

    // Require this knot syndicated
    require isKnotRegistered(k) && !isNoLongerPartOfSyndicate(k);

    mathint claimBefore = sETHUserClaimForKnot(k, e.msg.sender);
    mathint stakedBefore = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint calcBefore =  (accumulatedETHPerFreeFloatingShare() * stakedBefore) / 10^24;
    require calcBefore == claimBefore;

    claimAsStaker(e,addr,k);

    mathint claimAfter = sETHUserClaimForKnot(k, e.msg.sender);
    mathint stakedAfter = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint calcAfter =  (accumulatedETHPerFreeFloatingShare() * stakedAfter) / 10^24;

    assert stakedAfter == stakedBefore, "Stake should not change";
    assert stakedBefore >= 10^9 => claimAfter >= claimBefore
        // rounding error less than 10 gwei
        && -1 * 10^10 < calcAfter - claimAfter && calcAfter - claimAfter < 10^10 ,
        "Unexpected claim amount , rounding error too big ?";
}
