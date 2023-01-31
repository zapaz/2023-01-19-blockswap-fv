import "../Syndicate.spec"

// sETHTotalStakeForKnot and sETHUserClaimForKnot not allways increase ?!
rule alwaysIncrease(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;
    bytes32 b; address a;

    mathint amount5Before = sETHTotalStakeForKnot(b);
    mathint amount6Before = sETHUserClaimForKnot(b,a);

    f(e, args);

    mathint amount5After  = sETHTotalStakeForKnot(b);
    mathint amount6After  = sETHUserClaimForKnot(b,a);

    assert amount5After  >= amount5Before;
    assert amount6After  >= amount6Before;
}

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
