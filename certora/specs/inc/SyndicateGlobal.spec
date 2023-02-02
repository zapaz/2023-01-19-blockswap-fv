using MocksETH as sETHToken

/// Needs large screen and fixed font ;-)

methods {
    //// Added methods
    ethBalanceOf                                                    (address)                               returns (uint256)   envfree

    sETHBalanceOf                                                   (bytes32, address)                      returns (uint256)   envfree
    sETHTotalSupply                                                 (bytes32)                               returns (uint256)   envfree

    lastSeenETHPerCollateralizedSlotPerKnot                         ()                                      returns (uint256)   envfree
    lastSeenETHPerFreeFloating                                      ()                                      returns (uint256)   envfree
    totalFreeFloatingShares                                         ()                                      returns (uint256)   envfree
    getUnprocessedETHForAllCollateralizedSlot                       ()                                      returns (uint256)   envfree
    numberOfRegisteredKnots                                         ()                                      returns (uint256)   envfree
    previewUnclaimedETHAsCollateralizedSlotOwner                    (address, bytes32)                      returns (uint256)   envfree

    calculateETHForFreeFloatingOrCollateralizedHolders              ()                                      returns (uint256)   envfree
    calculateNewAccumulatedETHPerCollateralizedShare                (uint256)                               returns (uint256)   envfree
    calculateCollateralizedETHOwedPerKnot                           ()                                      returns (uint256)   envfree
    calculateNewAccumulatedETHPerFreeFloatingShare                  ()                                      returns (uint256)   envfree

    isActive                                                        (bytes32)                               returns (bool)      envfree
    isNoLongerPartOfSyndicate                                       (bytes32)                               returns (bool)      envfree

    initialize                                                      (address,uint256,address[],bytes32[])

    updateAccruedETHPerShares                                       ()                                                         envfree
    lastAccumulatedETHPerFreeFloatingShare                          (bytes32)                                                  envfree

    //// Regular methods
    totalETHReceived                                                ()                                      returns (uint256)   envfree
    isKnotRegistered                                                (bytes32)                               returns (bool)      envfree
    stake                                                           (bytes32[],uint256[],address)
    unstake                                                         (address,address,bytes32[],uint256[])
    accumulatedETHPerFreeFloatingShare                              ()                                      returns (uint256)   envfree
    accumulatedETHPerCollateralizedSlotPerKnot                      ()                                      returns (uint256)   envfree
    totalClaimed                                                    ()                                      returns (uint256)   envfree

    //// Resolving external calls
	// stakeHouseUniverse
	stakeHouseKnotInfo                                              (bytes32)                               returns (address,address,address,uint256,uint256,bool)  => DISPATCHER(true)
    memberKnotToStakeHouse                                          (bytes32)                               returns (address)                                       => DISPATCHER(true)
    // stakeHouseRegistry
    getMemberInfo                                                   (bytes32)                               returns (address,uint256,uint16,bool)                   => DISPATCHER(true)
    // slotSettlementRegistry
	stakeHouseShareTokens                                           (address)                               returns (address)                                       => DISPATCHER(true)
	currentSlashedAmountOfSLOTForKnot                               (bytes32)                               returns (uint256)                                       => DISPATCHER(true)
	numberOfCollateralisedSlotOwnersForKnot                         (bytes32)                               returns (uint256)                                       => DISPATCHER(true)
	getCollateralisedOwnerAtIndex                                   (bytes32, uint256)                      returns (address)                                       => DISPATCHER(true)
	totalUserCollateralisedSLOTBalanceForKnot                       (address, address, bytes32)             returns (uint256)                                       => DISPATCHER(true)
    // sETH
    sETHToken.balanceOf                                             (address)                               returns (uint256)   envfree
    sETHToken.totalSupply                                           ()                                      returns (uint256)   envfree

    // ERC20
    name                                                            ()                                      returns (string)                                        => DISPATCHER(true)
    symbol                                                          ()                                      returns (string)                                        => DISPATCHER(true)
    decimals                                                        ()                                      returns (string)    envfree                              => DISPATCHER(true)
    totalSupply                                                     ()                                      returns (uint256)                                       => DISPATCHER(true)
    balanceOf                                                       (address)                               returns (uint256)   envfree                              => DISPATCHER(true)
    allowance                                                       (address,address)                       returns (uint)                                          => DISPATCHER(true)
    approve                                                         (address,uint256)                       returns (bool)                                          => DISPATCHER(true)
    transfer                                                        (address,uint256)                       returns (bool)                                          => DISPATCHER(true)
    transferFrom                                                    (address,address,uint256)               returns (bool)                                          => DISPATCHER(true)

    //// Harnessing
    // harnessed variables
    accruedEarningPerCollateralizedSlotOwnerOfKnot                  (bytes32,address)                       returns (uint256)   envfree
    totalETHProcessedPerCollateralizedKnot                          (bytes32)                               returns (uint256)   envfree
    sETHStakedBalanceForKnot                                        (bytes32,address)                       returns (uint256)   envfree
    sETHTotalStakeForKnot                                           (bytes32)                               returns (uint256)   envfree
    sETHUserClaimForKnot                                            (bytes32,address)                       returns (uint256)   envfree

    // harnessed functions
    deRegisterKnots                                                 (bytes32)
    deRegisterKnots                                                 (bytes32,bytes32)
    stake                                                           (bytes32,uint256,address)
    stake                                                           (bytes32,bytes32,uint256,uint256,address)
    unstake                                                         (address,address,bytes32,uint256)
    unstake                                                         (address,address,bytes32,bytes32,uint256,uint256)
    claimAsStaker                                                   (address,bytes32)
    claimAsStaker                                                   (address,bytes32,bytes32)
    claimAsCollateralizedSLOTOwner                                  (address,bytes32)
    claimAsCollateralizedSLOTOwner                                  (address,bytes32,bytes32)
    registerKnotsToSyndicate                                        (bytes32)
    registerKnotsToSyndicate                                        (bytes32,bytes32)
    addPriorityStakers                                              (address)
    addPriorityStakers                                              (address,address)
    batchUpdateCollateralizedSlotOwnersAccruedETH                   (bytes32)
    batchUpdateCollateralizedSlotOwnersAccruedETH                   (bytes32,bytes32)
}

/// We defined additional functions to get around the complexity of defining dynamic arrays in cvl. We filter them in
/// normal rules and invariants as they serve no purpose.
definition notHarnessCall(method f) returns bool =
       f.selector != batchUpdateCollateralizedSlotOwnersAccruedETH  (bytes32).selector
    && f.selector != batchUpdateCollateralizedSlotOwnersAccruedETH  (bytes32,bytes32).selector
    && f.selector != deRegisterKnots                                (bytes32).selector
    && f.selector != deRegisterKnots                                (bytes32,bytes32).selector
    && f.selector != stake                                          (bytes32,uint256,address).selector
    && f.selector != stake                                          (bytes32,bytes32,uint256,uint256,address).selector
    && f.selector != unstake                                        (address,address,bytes32,uint256).selector
    && f.selector != unstake                                        (address,address,bytes32,bytes32,uint256,uint256).selector
    && f.selector != claimAsStaker                                  (address,bytes32).selector
    && f.selector != claimAsStaker                                  (address,bytes32,bytes32).selector
    && f.selector != claimAsCollateralizedSLOTOwner                 (address,bytes32).selector
    && f.selector != claimAsCollateralizedSLOTOwner                 (address,bytes32,bytes32).selector
    && f.selector != registerKnotsToSyndicate                       (bytes32).selector
    && f.selector != registerKnotsToSyndicate                       (bytes32,bytes32).selector
    && f.selector != addPriorityStakers                             (address).selector
    && f.selector != addPriorityStakers                             (address,address).selector;
