import "inc/SyndicateGlobal.spec"


/**
* Check that after staking, sETH amount is transfered from user to contract
*/
rule stakingStake() {
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

/**
* Check claimAsStaker is conform to calculation, and that stake is unchanged
*/
rule stakingClaimAsStaker() {
    env e; bytes32 k; address addr;

    requireInvariant knotsSyndicatedCount();
    requireInvariant numberOfRegisteredKnotsInvariant();
    requireInvariant lastAccumulatedIsNoLongerSyndicated(k);

    // Require this knot syndicated
    require isKnotRegistered(k) && !isNoLongerPartOfSyndicate(k);

    uint256 claimBefore  = sETHUserClaimForKnot(k, e.msg.sender);
    uint256 stakedBefore = sETHStakedBalanceForKnot(k, e.msg.sender);
    uint256 calcBefore   =  (accumulatedETHPerFreeFloatingShare() * stakedBefore) / 10^24;
    require calcBefore  == claimBefore;

    claimAsStaker(e,addr,k);

    uint256 claimAfter   = sETHUserClaimForKnot(k, e.msg.sender);
    uint256 stakedAfter  = sETHStakedBalanceForKnot(k, e.msg.sender);
    uint256 calcAfter    =  (accumulatedETHPerFreeFloatingShare() * stakedAfter) / 10^24;

    assert stakedAfter  == stakedBefore, "Stake should not change";
    assert stakedBefore  < 10^9 => claimAfter == claimBefore, "Should have not claimed! not enough amount";
    assert stakedBefore >= 10^9 => claimAfter >= claimBefore && calcAfter == claimAfter ,
        "Unexpected claim amount , rounding error too big ?";
}
