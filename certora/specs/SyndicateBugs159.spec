
import "inc/SyndicateGlobal.spec"

/**
* Minimum rule derived from unstakeRule to detect bug1
*/
rule bug1Rule() {
    env e; bytes32 key; uint256 amount;
    address ethTo; address unstaker;

    require amount              > 0;
    require unstaker           != currentContract;

    mathint sethToBalBefore     = sETHBalanceOf(key, unstaker);
    unstake(e, ethTo, unstaker, key, amount);
    mathint sethToBalAfter      = sETHBalanceOf(key, unstaker);

    assert sethToBalAfter      != sethToBalBefore;
}

/**
* Vacuous rule to detect bug5
*/
rule bug5Rule() {
    mathint knots  = numberOfRegisteredKnots();
    require knots != 0;

    assert getUnprocessedETHForAllCollateralizedSlot() ==
        ( ( totalETHReceived() / 2 ) - lastSeenETHPerCollateralizedSlotPerKnot()) / knots ;
}


/**
 * User Stake balance to Zero implies User Claim to Zero
 */
rule bug9Rule(){
    env e; bytes32 k; uint256 amount; address ethTo;

    mathint stakedBefore = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint claimBefore  = sETHUserClaimForKnot(k,e.msg.sender);

    require stakedBefore != 0;
    require claimBefore != 0;
    require amount > 10^12;

    unstake(e, e.msg.sender, ethTo, k, amount);

    mathint stakedAfter  = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint claimAfter   = sETHUserClaimForKnot(k,e.msg.sender);

    assert stakedAfter == 0 => claimAfter == 0,  "KO";
}