methods {
    increaseAllowance   (address,uint256)
    decreaseAllowance   (address,uint256)
    permit              (address,address,uint256,uint256,uint8,bytes32,bytes32)
}

rule integrityOfIncreaseAllowance(address spender, uint256 amount) {
	env e;
	uint256 allowanceBefore = allowance(e.msg.sender, spender);
	increaseAllowance(e, spender, amount);
	uint256 allowanceAfter = allowance(e.msg.sender, spender);

	assert amount > 0 => (allowanceAfter > allowanceBefore), "allowance did not increase";
    // Can you think of a way to strengthen this assert to account to all possible amounts?
}

rule changingAllowanceWithIncreaseDecrease(method f, address from, address spender)
    {
    require(decreaseAllowance(address, uint256).selector in currentContract);
    uint256 allowanceBefore = allowance(from, spender);
    env e;
    if (f.selector == approve(address, uint256).selector) {
        address spender_;
        uint256 amount;
        approve(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == transferFrom(address,address,uint256).selector) {
        address from_;
        address to;
        address amount;
        transferFrom(e, from_, to, amount);
        uint256 allowanceAfter = allowance(from, spender);
        if (from == from_ && spender == e.msg.sender) {
            assert from == to || allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
       } else if( f.selector == decreaseAllowance(address, uint256).selector) {
        address spender_;
        uint256 amount;
        require amount <= allowanceBefore;
        decreaseAllowance(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if ( f.selector == increaseAllowance(address, uint256).selector) {
        address spender_;
        uint256 amount;
        require amount + allowanceBefore < max_uint256;
        increaseAllowance(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == allowanceBefore + amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else {
        calldataarg args;
        f(e, args);
        assert allowance(from, spender) == allowanceBefore;
    }
}


rule changingAllowanceWithOutIncreaseDecrease(method f, address from, address spender)
    {
    require(!decreaseAllowance(address, uint256).selector in currentContract);
    uint256 allowanceBefore = allowance(from, spender);
    env e;
    if (f.selector == approve(address, uint256).selector) {
        address spender_;
        uint256 amount;
        approve(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == transferFrom(address,address,uint256).selector) {
        address from_;
        address to;
        address amount;
        transferFrom(e, from_, to, amount);
        uint256 allowanceAfter = allowance(from, spender);
        if (from == from_ && spender == e.msg.sender) {
            assert from == to || allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else {
        calldataarg args;
        f(e, args);
        assert allowance(from, spender) == allowanceBefore;
    }
}
