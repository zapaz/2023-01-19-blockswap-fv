import "inc/SyndicateGlobal.spec"

/**
* Check ETH solvency, that still claimable ETH is available in contract
*
* totalETHReceived     is the amount of ETH in contract and already claimed
* sETHUserClaimableSum is the amount of all claimable ETH (already claimed or still claimable)
*/
invariant ethSolvency()
    totalETHReceived() >= ghostSETHUserClaimableSum()
    filtered {
        f -> notHarnessCall(f)
        && f.selector != unstake(address,address,bytes32[],uint256[]).selector
        && f.selector != stake(bytes32[],uint256[],address).selector
        && f.selector != claimAsStaker(address,bytes32[]).selector
    }
    { preserved {
        requireInvariant knotsSyndicatedCount();
        requireInvariant numberOfRegisteredKnotsInvariant();
    }}

/**
* Increase amount of Total Claimed (when not 0) must be equal to amount of ETH decrease
*/
rule ethDecreaseWhenClaimedIncrease(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;

    mathint balBefore       = ethBalanceOf(currentContract);
    mathint claimedBefore   = totalClaimed();
    f(e, args);
    mathint balAfter        = ethBalanceOf(currentContract);
    mathint claimedAfter    = totalClaimed();

    assert claimedAfter > claimedBefore =>
            balBefore - balAfter == claimedAfter - claimedBefore, "ETH loss somewhere";
}
