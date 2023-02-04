import "inc/SyndicateGlobal.spec"

/**
* These public variables and functions() must allways increase
*
* accumulatedETHPerFreeFloatingShare
* accumulatedETHPerCollateralizedSlotPerKnot
¨* lastSeenETHPerCollateralizedSlotPerKnot
* lastSeenETHPerFreeFloating
*¨ totalClaimed
*
* totalETHReceived()
* calculateETHForFreeFloatingOrCollateralizedHolders()
*/
rule increasesAll(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;

    mathint amount1Before = accumulatedETHPerFreeFloatingShare();
    mathint amount2Before = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3Before = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount4Before = lastSeenETHPerFreeFloating();
    mathint amount5Before = totalClaimed();
    mathint amount6Before = totalETHReceived();
    mathint amount7Before = calculateETHForFreeFloatingOrCollateralizedHolders();

    f(e, args);

    mathint amount1After  = accumulatedETHPerFreeFloatingShare();
    mathint amount2After  = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3After  = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount4After  = lastSeenETHPerFreeFloating();
    mathint amount5After  = totalClaimed();
    mathint amount6After  = totalETHReceived();
    mathint amount7After  = calculateETHForFreeFloatingOrCollateralizedHolders();

    assert amount1After  >= amount1Before;
    assert amount2After  >= amount2Before;
    assert amount3After  >= amount3Before;
    assert amount4After  >= amount4Before;
    assert amount5After  >= amount5Before;
    assert amount6After  >= amount6Before;
    assert amount7After  >= amount7Before;
}
