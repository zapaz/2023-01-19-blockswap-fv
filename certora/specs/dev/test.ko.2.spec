import "../Syndicate.spec"


/**
* Check on Unstake that when ETH stake decrease
* (with reasonable values) claim amount decrease too
*/
rule sETHClaimDecreaseWithSETHStaked() {
    env e; bytes32 k; uint256 amount;
    address ethTo;

    mathint stakedBefore = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint claimBefore  = sETHUserClaimForKnot(k,e.msg.sender);

    // set some 'reasonable' values
    // on too big values rounding can make claimAfter == claimBefore
    require amount > 10¨^12;
    require lastSeenETHPerFreeFloating() < 10¨^36;
    require totalClaimed() < 10¨^36;
    require totalFreeFloatingShares() == 1;
    unstake(e, e.msg.sender, ethTo, k, amount);

    mathint stakedAfter  = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint claimAfter   = sETHUserClaimForKnot(k,e.msg.sender);

    assert stakedAfter < stakedBefore => claimAfter < claimBefore,  "KO";
}
