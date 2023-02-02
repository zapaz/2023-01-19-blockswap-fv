import "../Syndicate.spec"

// https://prover.certora.com/output/77791/7c3fadab96574784a76d47c175d45bf7/?anonymousKey=e80409f61f401bff20ec44b4b4086555c7d1ac9e

rule sETHUserClaimForKnotDecrease(){
    env e; bytes32 k; address addr;
    uint256 amount; address ethTo; address unstaker;

    require amount > 10^10;

    updateAccruedETHPerShares();

    uint256 claimBefore = sETHUserClaimForKnot(k,addr);

    unstake(e, ethTo, unstaker, k, amount);

    uint256 claimAfter  = sETHUserClaimForKnot(k,addr);

    assert claimAfter < claimBefore;
}
