
import "inc/SyndicateGlobal.spec"

/**
* Minimum rule derived from unstakeRule to detect bug1
*/
rule bug1Rule() {
    env e; bytes32 key; uint256 amount;
    address ethTo; address unstaker;

    require amount              > 0;
    require unstaker           != currentContract;

    mathint sethToBalBefore     = sETHBalanceOf(key, unstaker);
    unstake(e, ethTo, unstaker, key, amount);
    mathint sethToBalAfter      = sETHBalanceOf(key, unstaker);

    assert sethToBalAfter      != sethToBalBefore;
}

/**
* Vacuous rule to detect bug5
*/
rule bug5Rule(method f) filtered {
   f -> notHarnessCall(f)
}{
    mathint knots  = numberOfRegisteredKnots();
    require knots != 0;

    assert getUnprocessedETHForAllCollateralizedSlot() ==
        ( ( totalETHReceived() / 2 ) - lastSeenETHPerCollateralizedSlotPerKnot()) / knots ;
}
