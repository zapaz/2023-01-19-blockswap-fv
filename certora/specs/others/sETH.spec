import "ERC20.spec"

methods {
    mint   (address,uint256)
    burn   (address,uint256)
}

rule totalSupplyUnchanged(method f) filtered {
        f ->    f.selector != mint          (address,uint256)           .selector &&
                f.selector != burn          (address,uint256)           .selector
    }{
    env e; calldataarg args;

    mathint totalSupplyBefore = totalSupply();
    f(e, args);
    mathint totalSupplyAfter = totalSupply();

    assert totalSupplyAfter == totalSupplyBefore,
         "Total supply changed unexpectedly";
}

rule balanceOfUnchanged(method f, address user) filtered {
        f ->    f.selector != mint          (address,uint256)           .selector &&
                f.selector != burn          (address,uint256)           .selector &&
                f.selector != transfer      (address,uint256)           .selector &&
                f.selector != transferFrom  (address,address,uint256)   .selector
    }{
    env e; calldataarg args;

    uint256 userBalanceBefore = balanceOf(user);
    f(e, args);
    uint256 userBalanceAfter = balanceOf(user);

    assert userBalanceBefore == userBalanceAfter,
         "User's balance changed unexpectedly";
}

rule OtherBalanceOnlyGoesUp(address other, method f) {
    env e;
    uint256 balanceBefore = balanceOf(other);

    if (f.selector == transferFrom(address, address, uint256).selector) {
        address from;
        address to;
        uint256 amount;
        require(other != from);
        require balanceOf(from) + balanceBefore < max_uint256;
        transferFrom(e, from, to, amount);
    } else if (f.selector == transfer(address, uint256).selector) {
        require other != e.msg.sender;
        require balanceOf(e.msg.sender) + balanceBefore < max_uint256;
        calldataarg args;
        f(e, args);
    } else {
        require other != e.msg.sender;
        calldataarg args;
        f(e, args);
    }
    uint256 balanceAfter = balanceOf(other);

    assert balanceAfter < balanceBefore => f.selector == burn(address, uint256).selector,
         "Other's balance decreased unexpectedly";
}
