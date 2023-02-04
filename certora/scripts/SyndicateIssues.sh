certoraRun  certora/harnesses/SyndicateHarnessPlus.sol               \
    certora/harnesses/MockStakeHouseUniverse.sol                     \
    certora/harnesses/MockStakeHouseRegistry.sol                     \
    certora/harnesses/MockSlotSettlementRegistry.sol                 \
    certora/harnesses/MocksETH.sol                                   \
    certora/harnesses/MocksETH3.sol                                  \
    --verify SyndicateHarnessPlus:certora/specs/SyndicateIssues.spec \
    --cloud master                                                   \
    --optimistic_loop                                                \
    --optimize 1                                                     \
    --loop_iter 3                                                    \
    --rule_sanity                                                    \
    --settings -optimisticFallback=true                              \
    --packages                                                       \
    @blockswaplab=node_modules/@blockswaplab                         \
    @openzeppelin=node_modules/@openzeppelin                         \
    --msg "Syndicate Issues $1"                                      \
