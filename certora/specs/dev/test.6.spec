import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant

/**
* Check ETH solvency, that still claimable ETH is available in contract
*
* totalETHReceived     is the amount of ETH in contract and already claimed
* sETHUserClaimableSum is the amount of all claimable ETH (already claimed or still claimable)
*/
invariant ethSolvency()
    totalETHReceived() >= ghostSETHUserClaimableSum()
    filtered { f -> notHarnessCall(f) }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    }}


/**
* Check calculation function on amount of ETH eligible for free floating or collateralized holders
*
* Half of total ETH received should eligible for free floating or collateralized holders
*/
invariant ethEligible()
    calculateETHForFreeFloatingOrCollateralizedHolders() == totalETHReceived() / 2
    filtered { f -> notHarnessCall(f) }
