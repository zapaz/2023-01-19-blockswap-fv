import "../Syndicate.spec"

rule test3() {
    bytes32 k; address addr;
    // active knot
    require isKnotRegistered(k) && !isNoLongerPartOfSyndicate(k);

    mathint claim = sETHUserClaimForKnot(k)(addr);
    mathint calc =  accumulatedETHPerFreeFloatingShare() * sETHStakedBalanceForKnot(k)(addr) / PRECISION;

    assert claim  == calc, "ERR";
}