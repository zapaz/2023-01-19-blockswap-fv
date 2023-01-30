import "inc/SyndicateGlobal.spec"

//  mapping(bytes32 => bool) public isKnotRegistered
ghost ghostKnotsRegisteredCount() returns uint256 {
    init_state axiom ghostKnotsRegisteredCount() == 0;
}
hook Sstore isKnotRegistered[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsRegisteredCount assuming ghostKnotsRegisteredCount@new() ==
        ghostKnotsRegisteredCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

// mapping(bytes32 => bool) public isNoLongerPartOfSyndicate
ghost ghostKnotsNotSyndicatedCount() returns uint256 {
    init_state axiom ghostKnotsNotSyndicatedCount() == 0;
}
hook Sstore isNoLongerPartOfSyndicate[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsNotSyndicatedCount assuming ghostKnotsNotSyndicatedCount@new() ==
        ghostKnotsNotSyndicatedCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

invariant knotsSyndicatedCount()
    numberOfRegisteredKnots() == ghostKnotsRegisteredCount() - ghostKnotsNotSyndicatedCount()
    filtered { f -> notHarnessCall(f) }

/**
 * An unregistered knot can not be deregistered.
 */
rule knotsCanNotDeregisterUnregistered(){
    bytes32 knot; env e;

    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}