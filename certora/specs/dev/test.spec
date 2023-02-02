import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant

/**
* Check the amount of all claimable ETH is more that total amount already claimed
*/
invariant sETHTotalClaimable()
    ghostSETHUserClaimableSum() >= totalClaimed()
    filtered {
        f -> notHarnessCall(f)
        && f.selector != unstake(address,address,bytes32[],uint256[]).selector
        && f.selector != claimAsCollateralizedSLOTOwner(address,bytes32[]).selector
    }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    } }

/**
* Check ETH solvency, that still claimable ETH is available in contract
*
* totalETHReceived     is the amount of ETH in contract and already claimed
* sETHUserClaimableSum is the amount of all claimable ETH (already claimed or still claimable)
*/
invariant ethSolvency()
    totalETHReceived() >= ghostSETHUserClaimableSum()
    filtered {
        f -> notHarnessCall(f)
        && f.selector != unstake(address,address,bytes32[],uint256[]).selector
        && f.selector != stake(bytes32[],uint256[],address).selector
        && f.selector != claimAsStaker(address,bytes32[]).selector
    }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    }}
