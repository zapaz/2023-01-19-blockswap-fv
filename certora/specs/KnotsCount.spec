import "inc/SyndicateGlobal.spec"

// mapping(bytes32 => bool) public isNoLongerPartOfSyndicate
ghost isNoLongerPartOfSyndicateCount() returns uint256 {
    init_state axiom isNoLongerPartOfSyndicateCount() == 0;
}
hook Sstore isNoLongerPartOfSyndicate[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc isNoLongerPartOfSyndicateCount assuming isNoLongerPartOfSyndicateCount@new() == isNoLongerPartOfSyndicateCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

//  mapping(bytes32 => bool) public isKnotRegistered
ghost isKnotRegisteredCount() returns uint256 {
    init_state axiom isKnotRegisteredCount() == 0;
}
hook Sstore isKnotRegistered[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc isKnotRegisteredCount assuming isKnotRegisteredCount@new() == isKnotRegisteredCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

invariant numberOfRegisteredKnotsInvariant()
    numberOfRegisteredKnots() == isKnotRegisteredCount() - isNoLongerPartOfSyndicateCount()
    filtered { f -> notHarnessCall(f) }
