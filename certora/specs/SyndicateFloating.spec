import "inc/SyndicateGlobal.spec"

invariant lastAccumulatedIsNoLongerSyndicated(bytes32 k)
  lastAccumulatedETHPerFreeFloatingShare(k) > 0 => isNoLongerPartOfSyndicate(k)
    filtered { f -> notHarnessCall(f) }
