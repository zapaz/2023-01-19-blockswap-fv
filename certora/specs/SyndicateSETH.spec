import "inc/SyndicateGlobal.spec"

// ghostSETHTotalStaked() <=> mapping(bytes32 => mapping(address => uint256)) public sETHStakedBalanceForKnot
ghost ghostSETHTotalStaked() returns uint256 {
    init_state axiom ghostSETHTotalStaked() == 0;
}
hook Sstore sETHStakedBalanceForKnot[KEY bytes32 k][KEY address a] uint256 newValue (uint256 oldValue) STORAGE {
    havoc ghostSETHTotalStaked assuming ghostSETHTotalStaked@new() == ghostSETHTotalStaked@old() + newValue - oldValue;
}

// ghostSETHTotalStaked2() <=> mapping(bytes32 => uint256) public sETHTotalStakeForKnot
ghost ghostSETHTotalStaked2() returns uint256 {
    init_state axiom ghostSETHTotalStaked2() == 0;
}
hook Sstore sETHTotalStakeForKnot[KEY bytes32 k] uint256 newValue (uint256 oldValue) STORAGE {
    havoc ghostSETHTotalStaked2 assuming ghostSETHTotalStaked2@new() == ghostSETHTotalStaked2@old() + newValue - oldValue;
}

invariant sETHTotalStakeForKnotInvariant()
    ghostSETHTotalStaked() == ghostSETHTotalStaked2()
    filtered { f -> notHarnessCall(f) }

// mapping(bytes32 => mapping(address => uint256)) public sETHUserClaimForKnot
ghost ghostSETHUserClaimableSum() returns uint256 {
    init_state axiom ghostSETHUserClaimableSum() == 0;
}
hook Sstore sETHUserClaimForKnot[KEY bytes32 k][KEY address a] uint256 newClaimed (uint256 oldClaimed) STORAGE {
    havoc ghostSETHUserClaimableSum assuming ghostSETHUserClaimableSum@new() == ghostSETHUserClaimableSum@old() + newClaimed - oldClaimed;
}

/**
 * Address 0 must have zero balance for any StakeHouse sETH
 */
invariant sETHAddressZeroHasNoBalance(bytes32 key)
    sETHBalanceOf(key, 0) == 0
    filtered { f -> notHarnessCall(f) }

/**
* Check the amount of all claimable ETH is more that amount already claimed
*/
invariant ethTotalClaimable()
    ghostSETHUserClaimableSum() >= totalClaimed()
    filtered { f -> notHarnessCall(f) }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    } }

/**
 * Sum of two balances is allways less than Total :
 * Given one user, for any other random user making whatever calls,
 * their combined sETH balances stays less than Total
 */
invariant sETHSolvencyCorrollary(address user, address random, bytes32 knot)
    random != user => sETHStakedBalanceForKnot(knot, user) +
                      sETHStakedBalanceForKnot(knot, random) <= sETHTotalStakeForKnot(knot)
    filtered { f -> notHarnessCall(f) }
    {
        preserved with(env e) {
            require e.msg.sender == random;
        }
    }
