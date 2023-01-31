import "../Syndicate.spec"

rule test42(){
    require numberOfRegisteredKnots() == 0;
    require knotRegisteredCount() == 0;
    require noLongerPartOfSyndicateCount() == 0;

    env e; calldataarg args;
    initialize(e,args);
    // initialize@withrevert(e,args);
    // assert !lastReverted , "Initalize allways reverts";
    assert numberOfRegisteredKnots() == knotRegisteredCount() - noLongerPartOfSyndicateCount();
}
