import "../Syndicate.spec"

invariant noEthWhenNotValid(bytes32 b)
    !isActive(b) => totalETHProcessedPerCollateralizedKnot(b) == 0
    filtered { f -> notHarnessCall(f) }

rule stakeTwice(){
    env e1; bytes32 key1;
    env e2; bytes32 key2;
    require e1.msg.sender != currentContract;
    require e2.msg.sender != currentContract;
    require key1 != key2;

    uint256 amount = 10000000000000000000;
    address behalf;

    uint256 maxBefore = sETHToken.totalSupply();
    require maxBefore <= 12000000000000000000;

    stake(e1, key1, amount, behalf);

    uint256 maxBetween = sETHToken.totalSupply();

    stake(e2, key2, amount, behalf);

    uint256 maxAfter = sETHToken.totalSupply();
    assert maxAfter <= 12000000000000000000;
    assert false;
}
