import "../Syndicate.spec"

/**
* accumulatedETHPerCollateralizedSlotPerKnot is n times than lastSeenETHPerCollateralizedSlotPerKnot
*/
rule accLast(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;

    mathint amount1Before  = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount2Before  = lastSeenETHPerCollateralizedSlotPerKnot();
    require amount1Before == amount2Before;

    f(e, args);

    mathint amount1After   = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount2After   = lastSeenETHPerCollateralizedSlotPerKnot();

    assert amount1After   == amount2After;
}
