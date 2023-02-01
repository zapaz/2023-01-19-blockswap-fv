import "inc/SyndicateGlobal.spec"

/**
* Ghost function with associated Hook equal to public variable numberOfRegisteredKnots
*
* related solidity declaration : uint256 public numberOfRegisteredKnots;
*/
ghost ghostNumberOfRegisteredKnots() returns uint256 {
    init_state axiom ghostNumberOfRegisteredKnots() == 0;
}
hook Sstore numberOfRegisteredKnots uint256 num STORAGE {
    havoc ghostNumberOfRegisteredKnots assuming ghostNumberOfRegisteredKnots@new() == num;
}

/**
* Ghost function with associated Hook equal to the number of registered Knots
* following isKnotRegistered mapping
*
* related solidity declaration : mapping(bytes32 => bool) public isKnotRegistered;
*/
ghost ghostKnotsRegisteredCount() returns uint256 {
    init_state axiom ghostKnotsRegisteredCount() == 0;
}
hook Sstore isKnotRegistered[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsRegisteredCount assuming ghostKnotsRegisteredCount@new() ==
        ghostKnotsRegisteredCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

/**
* Ghost function with associated Hook equal to the number of Knots no longer Syndicated
* following isNoLongerPartOfSyndicate mapping
*
* related solidity declaration : mapping(bytes32 => bool) public isNoLongerPartOfSyndicate;
*/
ghost ghostKnotsNotSyndicatedCount() returns uint256 {
    init_state axiom ghostKnotsNotSyndicatedCount() == 0;
}
hook Sstore isNoLongerPartOfSyndicate[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsNotSyndicatedCount assuming ghostKnotsNotSyndicatedCount@new() ==
        ghostKnotsNotSyndicatedCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

/**
 * Ghost function on numberOfRegisteredKnots variable must always be equal
 * to public getter function numberOfRegisteredKnots()
 *
 * Invariant needed on some rules, to ensure ghost is well initialized
 */
invariant numberOfRegisteredKnotsInvariant()
    numberOfRegisteredKnots() == ghostNumberOfRegisteredKnots()
    filtered { f -> notHarnessCall(f) }

/**
 * Knots count invariants : numberOfRegisteredKnots must be equal to
 * the number of registered Knots minus those registered
 * who are no longer part of the Syndicated
 *
 * numberOfRegisteredKnots name is misleading:
 * it's not the number of Knots registerer
 * but the number of Knots registered and not syndicated
 * it could be renamed to numberOSyndicatedKnots
 */
invariant knotsSyndicatedCount()
    numberOfRegisteredKnots() == ghostKnotsRegisteredCount() - ghostKnotsNotSyndicatedCount()
    filtered { f -> notHarnessCall(f) }

/**
 * Rule to check that an unregistered Knot can not be deregistered.
 */
rule knotsCanNotDeregisterUnregistered(){
    bytes32 knot; env e;

    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}