import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant

/**
* Check ETH solvency, that all claimable ETH are available in contract
*
* totalETHReceived     is the amount of ETH in contract and already claimed
* sETHUserClaimableSum is the amount of all claimable ETH (already claimed or still claimable)
*/
rule ethSolvency2() {
    env e; address ethTo; address unstaker;
    bytes32 key; uint256 amount;

    require lastSeenETHPerFreeFloating()                 < 10^36;
    require lastSeenETHPerCollateralizedSlotPerKnot()    < 10^36;
    require accumulatedETHPerFreeFloatingShare()         < 10^36;
    require accumulatedETHPerCollateralizedSlotPerKnot() < 10^36;
    require totalFreeFloatingShares()                    < 10^12;
    require numberOfRegisteredKnots()                    < 10^12;

    requireInvariant knotsSyndicatedCount();
    requireInvariant numberOfRegisteredKnotsInvariant();

    require totalETHReceived() < 10^36;
    require totalETHReceived() > 10^12;
    require totalETHReceived() >= ghostSETHUserClaimableSum();
    require unstaker != currentContract;
    unstake(e, ethTo, unstaker, key, amount);

    assert totalETHReceived() + 10 >= ghostSETHUserClaimableSum();
}

rule ethSolvency3() {
    env e; address ethTo; address unstaker;
    bytes32 key; uint256 amount;

    requireInvariant knotsSyndicatedCount();
    requireInvariant numberOfRegisteredKnotsInvariant();

    require totalETHReceived() >= ghostSETHUserClaimableSum();
    require unstaker != currentContract;

    unstake(e, ethTo, unstaker, key, amount);

    assert totalETHReceived()  >= ghostSETHUserClaimableSum();
}
