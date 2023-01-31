import "../Syndicate.spec"

use invariant numberOfRegisteredKnotsInvariant

invariant ghostNumberOfRegisteredKnotsInvariant()
    ghostNumberOfRegisteredKnots() == ghostKnotsRegisteredCount() - ghostKnotsNotSyndicatedCount()
    filtered { f -> notHarnessCall(f) }
    { preserved {
            requireInvariant numberOfRegisteredKnotsInvariant();
    } }
