import "inc/SyndicateGlobal.spec"

/**
* On stake, sETH amount is transfered from user to contract
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
* On unstake, sETH amount is transfered from contract to user
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
