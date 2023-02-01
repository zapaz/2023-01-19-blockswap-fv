import "inc/SyndicateGlobal.spec"


/**
* Increase amount of Total Claimed (when not 0) must be equal to amount of ETH decrease
*/
rule ethDecreaseWhenClaimedIncrease(method f){
    env e; calldataarg args;

    mathint balBefore       = ethBalance();
    mathint claimedBefore   = totalClaimed();
    f(e, args);
    mathint balAfter        = ethBalance();
    mathint claimedAfter    = totalClaimed();

    assert claimedAfter > claimedBefore =>
            balBefore - balAfter == claimedAfter - claimedBefore, "ETH loss somewhere";
}