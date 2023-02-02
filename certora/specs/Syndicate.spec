import "inc/SyndicateGlobal.spec"
import "SyndicateBugs159.spec"
import "SyndicateETH.spec"
import "SyndicateFloating.spec"
import "SyndicateIncreases.spec"
import "SyndicateKnots.spec"
import "SyndicateSETH.spec"
import "SyndicateStaking.spec"

use rule     bug1Rule
use rule     bug5Rule
use rule     bug9Rule

use invariant ethSolvency
use rule      ethDecreaseWhenClaimedIncrease

use invariant lastAccumulatedIsNoLongerSyndicated

use rule      increasesAll

use invariant numberOfRegisteredKnotsInvariant
use invariant knotsSyndicatedCount
use rule     knotsCanNotDeregisterUnregistered

use invariant sETHTotalStakeForKnotInvariant
use invariant sETHAddressZeroHasNoBalance
use invariant sETHSolvencyCorrollary
use invariant sETHSTloatingShareTotalEqualSum
use invariant sETHSTloatingShareTotalLessThanSum
use invariant sETHBalanceZeroThenClaimAlso
use invariant sETHTotalClaimable
use rule     sETHUserClaimForKnotIncrease

use rule     stakingStake
use rule     stakingUnstake
use rule     stakingClaimAsStaker