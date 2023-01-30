import "inc/SyndicateGlobal.spec"

/**
* AccumulatedETH, totalClaimed and totalETHReceived allways increase
*/
rule increasesAll(method f) filtered {
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
