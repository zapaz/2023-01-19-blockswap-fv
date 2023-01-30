import "inc/SyndicateGlobal.spec"


/**
* Change of claimed total is equal to ETH increase
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