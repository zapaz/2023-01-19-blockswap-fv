import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant

invariant ethSolvency()
    totalETHReceived() >= ghostSETHUserClaimableSum()
    filtered { f -> notHarnessCall(f) }
    { preserved {
        bytes32 k;
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    }}
