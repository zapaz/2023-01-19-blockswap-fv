import "inc/SyndicateGlobal.spec"

methods {
    numberOfRegisteredKnots                         ()                  returns (uint256)   envfree
    getUnprocessedETHForAllCollateralizedSlot       ()                  returns (uint256)   envfree
    previewUnclaimedETHAsCollateralizedSlotOwner    (address, bytes32)  returns (uint256)   envfree
    calculateNewAccumulatedETHPerFreeFloatingShare  ()                  returns (uint256)   envfree
    totalFreeFloatingShares                         ()                  returns (uint256)   envfree
}

rule zeroDivOnZeroKnot1(method f) filtered {
    f -> notHarnessCall(f)
}{
    mathint n = numberOfRegisteredKnots();
    require n == 0;

    mathint acc = getUnprocessedETHForAllCollateralizedSlot@withrevert();

    assert !lastReverted , "getUnprocessedETHForAllCollateralizedSlot should not revert with zero registered knots";
}

rule zeroDivOnZeroKnot2(method f) filtered {
    f -> notHarnessCall(f)
}{
    mathint n = numberOfRegisteredKnots();
    require n == 0;

    calldataarg args;
    mathint acc = previewUnclaimedETHAsCollateralizedSlotOwner@withrevert(args);

    assert !lastReverted , "previewUnclaimedETHAsCollateralizedSlotOwner should not revert with zero registered knot";
}

rule zeroDivOnZeroFloatingShare(method f) filtered {
    f -> notHarnessCall(f)
}{
    mathint t = totalFreeFloatingShares();
    require t == 0;

    calldataarg args;
    mathint acc = calculateNewAccumulatedETHPerFreeFloatingShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerFreeFloatingShare should not revert with zero floating share";
}
