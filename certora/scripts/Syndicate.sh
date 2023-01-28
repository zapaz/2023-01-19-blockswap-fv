certoraRun  certora/harnesses/SyndicateHarness.sol               \
    certora/harnesses/MockStakeHouseUniverse.sol                  \
    certora/harnesses/MockStakeHouseRegistry.sol                  \
    certora/harnesses/MockSlotSettlementRegistry.sol              \
    certora/harnesses/MocksETH.sol                                \
    certora/harnesses/MocksETH2.sol                               \
    certora/harnesses/MocksETH3.sol                               \
    --verify SyndicateHarness:certora/specs/Syndicate.spec       \
    --cloud master                                                \
    --optimistic_loop                                             \
    --optimize 1                                                  \
    --loop_iter 3                                                 \
    --rule_sanity                                                 \
    --settings -optimisticFallback=true                           \
    --packages                                                    \
    @blockswaplab=node_modules/@blockswaplab                      \
    @openzeppelin=node_modules/@openzeppelin                      \
    --msg "Syndicate $1"                                          \
    # --typecheck_only                                              \
    # --rule $1
