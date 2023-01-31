#!/bin/bash

if [[ "$2" ]]
then
    RULE="--rule $2"
fi

# solc-select use 0.8.13
set -x

certoraRun  certora/harnesses/SyndicateHarness.sol                \
    certora/harnesses/MockStakeHouseUniverse.sol                  \
    certora/harnesses/MockStakeHouseRegistry.sol                  \
    certora/harnesses/MockSlotSettlementRegistry.sol              \
    certora/harnesses/MocksETH.sol                                \
    --verify SyndicateHarness:certora/specs/dev/test.spec         \
    --cloud master                                                \
    --optimistic_loop                                             \
    --optimize 1                                                  \
    --loop_iter 3                                                 \
    --rule_sanity                                                 \
    --send_only                                                   \
    --settings -optimisticFallback=true                           \
    --packages                                                    \
    @blockswaplab=node_modules/@blockswaplab                      \
    @openzeppelin=node_modules/@openzeppelin                      \
    $RULE                                                         \
    --msg "Syndicate $1 $2"                                       \
    --multi_assert_check                                          \
    # --typecheck_only                                              \
