import "inc/SyndicateGlobal.spec"

/**
* Divide by Zero Bug
*
* getUnprocessedETHForAllCollateralizedSlot() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot1(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    getUnprocessedETHForAllCollateralizedSlot@withrevert();

    assert !lastReverted , "getUnprocessedETHForAllCollateralizedSlot should not revert with zero registered knots";
}

/**
* Divide by Zero Bug
*
* previewUnclaimedETHAsCollateralizedSlotOwner() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot2(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    previewUnclaimedETHAsCollateralizedSlotOwner@withrevert(args);

    assert !lastReverted , "previewUnclaimedETHAsCollateralizedSlotOwner should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateNewAccumulatedETHPerCollateralizedShare() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot3(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateNewAccumulatedETHPerCollateralizedShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerCollateralizedShare should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateCollateralizedETHOwedPerKnot() reverts with zero registered knots
*/
rule zeroDivOnZeroKnot4(calldataarg args){
    require numberOfRegisteredKnots() == 0;

    calculateCollateralizedETHOwedPerKnot@withrevert(args);

    assert !lastReverted , "calculateCollateralizedETHOwedPerKnot should not revert with zero registered knot";
}

/**
* Divide by Zero Bug
*
* calculateNewAccumulatedETHPerFreeFloatingShare() reverts with zero floating share
*/
rule zeroDivOnZeroFloatingShare(calldataarg args){
    require totalFreeFloatingShares() == 0;

    calculateNewAccumulatedETHPerFreeFloatingShare@withrevert(args);

    assert !lastReverted , "calculateNewAccumulatedETHPerFreeFloatingShare should not revert with zero floating share";
}


