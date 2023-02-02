import "../Syndicate.spec"


/**
* Check that after staking, sETH amount is transfered from user to contract
*/
rule stakingStake() {
    env e; bytes32 key; uint256 amount; address behalf;

    address staker  = e.msg.sender;
    require  staker != currentContract;

    mathint totalBefore        = totalFreeFloatingShares();
    mathint stakerBalBefore    = sETHBalanceOf(key, staker);
    mathint syndicateBalBefore = sETHBalanceOf(key, currentContract);

    stake(e, key, amount, behalf);

    mathint totalAfter         = totalFreeFloatingShares();
    mathint stakerBalAfter     = sETHBalanceOf(key, staker);
    mathint syndicateBalAfter  = sETHBalanceOf(key, currentContract);

    assert stakerBalAfter    == stakerBalBefore    - amount;
    assert syndicateBalAfter == syndicateBalBefore + amount;
    assert totalAfter        == totalBefore + amount;
}
