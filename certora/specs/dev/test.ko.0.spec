/**
* Check the amount of all claimable ETH is more that amount already claimed
*/
invariant sETHTotalClaimable()
    ghostSETHUserClaimableSum() >= totalClaimed()
    filtered { f -> notHarnessCall(f) }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    } }
