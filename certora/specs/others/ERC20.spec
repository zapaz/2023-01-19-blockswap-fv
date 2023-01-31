methods {
    name                ()                          returns (string)    envfree
    symbol              ()                          returns (string)    envfree
    decimals            ()                          returns (uint8)     envfree
    totalSupply         ()                          returns (uint256)   envfree
    balanceOf           (address)                   returns (uint256)   envfree
    transfer            (address,uint256)           returns (bool)
    transferFrom        (address,address,uint256)   returns (bool)
    approve             (address,uint256)           returns (bool)
    allowance           (address,address)           returns (uint256)   envfree
}

definition globalInvariant(env e) returns bool =
  e.msg.sender != 0;

invariant ZeroAddressNoBalance()
  balanceOf(0) == 0
//   { preserved with (env e) { requireInvariant globalInvariant(e); } }


rule transferIntegrity(address to, uint256 amount) {
    env e;
    address from = e.msg.sender;

    mathint balanceOfFromBefore = balanceOf(from);
    mathint balanceOfToBefore = balanceOf(to);
    require balanceOfFromBefore + balanceOfToBefore < max_uint256;

    transfer(e, to, amount);

    mathint balanceOfFromAfter = balanceOf(from);
    mathint balanceOfToAfter = balanceOf(to);

    assert from != to =>
        balanceOfFromAfter == balanceOfFromBefore - amount &&
        balanceOfToAfter == balanceOfToBefore + amount;

    assert from == to => balanceOfToAfter == balanceOfToBefore;
}

rule transferFromIntegrity(address from, address to, uint256 amount) {
    env e;

    mathint balanceOfFromBefore = balanceOf(from);
    mathint balanceOfToBefore = balanceOf(to);
    mathint allowanceBefore = allowance(from, e.msg.sender);
    require balanceOfFromBefore + balanceOfToBefore <= max_uint256;

    transferFrom(e, from, to, amount);

    mathint balanceOfFromAfter = balanceOf(from);
    mathint balanceOfToAfter = balanceOf(to);
    mathint allowanceAfter = allowance(from, e.msg.sender);

    assert from != to =>
        balanceOfFromAfter  == balanceOfFromBefore - amount &&
        balanceOfToAfter    == balanceOfToBefore   + amount &&
        allowanceAfter      == allowanceBefore     - amount ;

    assert from == to =>
        balanceOfToAfter    == balanceOfToBefore &&
        allowanceAfter      == allowanceBefore   ;
}

rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
    env e; /* a representation of the calling context (msg.sender, block.timestamp, ... ) */
    require alice != bob; /* without this require you will get a counter example in which alice and bob are the same address  */
    require allowance(alice, e.msg.sender) >= amount;
    uint256 balanceBefore = balanceOf(bob);

    transferFrom(e, alice, bob, amount);

    uint256 balanceAfter = balanceOf(bob);
    assert balanceAfter == balanceBefore + amount;
}

rule noFeeOnTransfer(address bob, uint256 amount) {
    env e;
    require bob != e.msg.sender;
    uint256 balanceSenderBefore = balanceOf(e.msg.sender);
    uint256 balanceBefore = balanceOf(bob);

    transfer(e, bob, amount);

    uint256 balanceAfter = balanceOf(bob);
    uint256 balanceSenderAfter = balanceOf(e.msg.sender);
    assert balanceAfter == balanceBefore + amount;
}


rule transferFromReverts(address from, address to, uint256 amount) {
    env e;
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    uint256 fromBalanceBefore = balanceOf(from);
    require from != 0 && e.msg.sender != 0;
    require e.msg.value == 0;
    require fromBalanceBefore + balanceOf(to) <= max_uint256;

    transferFrom@withrevert(e, from, to, amount);

    assert lastReverted <=> (allowanceBefore < amount || amount > fromBalanceBefore || to == 0);
}

rule transferReverts(address from, address to, uint256 amount) {
    env e;
    uint256 fromBalanceBefore = balanceOf(e.msg.sender);
    require e.msg.sender != 0;
    require e.msg.value == 0;
    require fromBalanceBefore + balanceOf(to) <= max_uint256;

    transfer@withrevert(e, to, amount);

    assert lastReverted <=> ( amount > fromBalanceBefore || to == 0);
}

rule transferSumOfFromAndToBalancesStaySame(address to, uint256 amount) {
    env e;
    mathint sum = balanceOf(e.msg.sender) + balanceOf(to);
    require sum < max_uint256;
    transfer(e, to, amount);
    assert balanceOf(e.msg.sender) + balanceOf(to) == sum;
}

rule transferFromSumOfFromAndToBalancesStaySame(address from, address to, uint256 amount) {
    env e;
    mathint sum = balanceOf(from) + balanceOf(to);
    require sum < max_uint256;
    transferFrom(e, from, to, amount);
    assert balanceOf(from) + balanceOf(to) == sum;
}

rule transferDoesntChangeOtherBalance(address to, uint256 amount, address other) {
    env e;
    require other != e.msg.sender;
    require other != to;
    uint256 balanceBefore = balanceOf(other);
    transfer(e, to, amount);
    assert balanceBefore == balanceOf(other);
}

rule transferFromDoesntChangeOtherBalance(address from, address to, uint256 amount, address other) {
    env e;
    require other != from;
    require other != to;
    uint256 balanceBefore = balanceOf(other);
    transferFrom(e, from, to, amount);
    assert balanceBefore == balanceOf(other);
}


rule transferShouldReturnTrue(address other, method f) {
    env e;
    calldataarg args;
    bool ret = transfer@withrevert(e,args);
    assert !lastReverted => ret;
}
