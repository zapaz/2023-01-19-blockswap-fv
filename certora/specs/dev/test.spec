import "../Syndicate.spec"

rule sETHUserClaimForKnotDecrease(){
    env e; bytes32 k; address addr;
    uint256 amount; address ethTo; address unstaker;

    updateAccruedETHPerShares();

    uint256 claimBefore = sETHUserClaimForKnot(k,addr);

    unstake(e, ethTo, unstaker, k, amount);

    uint256 claimAfter  = sETHUserClaimForKnot(k,addr);

    assert amount > 0 => claimAfter < claimBefore;
}
