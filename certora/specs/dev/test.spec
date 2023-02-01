import "../Syndicate.spec"

use invariant knotsSyndicatedCount
use invariant numberOfRegisteredKnotsInvariant
use invariant lastAccumulatedIsNoLongerSyndicated

// sETHUserClaimForKnot not allways increase ?!
rule alwaysIncrease(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;
    bytes32 k; address addr;

    mathint amountBefore = sETHUserClaimForKnot(k,addr);

    f(e, args);

    mathint amountAfter  = sETHUserClaimForKnot(k,addr);

    assert amountAfter  >= amountBefore;
}
