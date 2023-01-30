import "inc/SyndicateGlobal.spec"

rule zeroDivOnZeroKnot1(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    getUnprocessedETHForAllCollateralizedSlot@withrevert();

    assert !lastReverted , "getUnprocessedETHForAllCollateralizedSlot should not revert with zero registered knots";
}

rule zeroDivOnZeroKnot2(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    previewUnclaimedETHAsCollateralizedSlotOwner@withrevert(args);

    assert !lastReverted , "previewUnclaimedETHAsCollateralizedSlotOwner should not revert with zero registered knot";
}

rule zeroDivOnZeroKnot3(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateNewAccumulatedETHPerCollateralizedShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerCollateralizedShare should not revert with zero registered knot";
}

rule zeroDivOnZeroKnot4(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateCollateralizedETHOwedPerKnot@withrevert(args);

    assert !lastReverted , "calculateCollateralizedETHOwedPerKnot should not revert with zero registered knot";
}

rule zeroDivOnZeroFloatingShare(calldataarg args){
    require totalFreeFloatingShares() == 0;

    calculateNewAccumulatedETHPerFreeFloatingShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerFreeFloatingShare should not revert with zero floating share";
}
