import "../Syndicate.spec"


rule alwaysIncrease2(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;
    bytes32 b;

    mathint amount4Before = totalETHProcessedPerCollateralizedKnot(b);
    f(e, args);
    mathint amount4After = totalETHProcessedPerCollateralizedKnot(b);

    assert amount4After >= amount4Before;
}
