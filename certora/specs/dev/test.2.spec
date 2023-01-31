import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant

invariant sETHSTloatingShareTotalLessThanSum()
    ghostSETHTotalStaked() >= totalFreeFloatingShares()
    filtered { f -> notHarnessCall(f) }
    { preserved {
            requireInvariant knotsSyndicatedCount();
            requireInvariant numberOfRegisteredKnotsInvariant();
    }}

invariant sETHSTloatingShareTotalEqualThanSum()
    ghostSETHTotalStaked() == totalFreeFloatingShares()
    filtered {
        f -> notHarnessCall(f)
        && f.selector != unstake(address,address,bytes32[],uint256[]).selector
        && f.selector != deRegisterKnots(bytes32[]).selector
        && f.selector != updateCollateralizedSlotOwnersAccruedETH(bytes32).selector
        && f.selector != claimAsCollateralizedSLOTOwner(address,bytes32[]).selector
        && f.selector != batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32[]).selector
    }
    { preserved {
            requireInvariant knotsSyndicatedCount();
            requireInvariant numberOfRegisteredKnotsInvariant();
    }}
