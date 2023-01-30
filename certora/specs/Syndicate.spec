import "inc/SyndicateGlobal.spec"
import "SyndicateBugs159.spec"
import "SyndicateIncreases.spec"
import "SyndicateStaking.spec"
import "SyndicateKnots.spec"
import "SyndicateETH.spec"
import "SyndicateSETH.spec"

use rule     bug1Rule
use rule     bug5Rule

use rule     increasesAll

use rule     stakingStake
use rule     stakingUnstake

use invariant knotsSyndicatedCount
use rule     knotsCanNotDeregisterUnregistered

use rule     ethDecreaseWhenClaimedIncrease

use invariant sETHTotalStakeForKnotInvariant
use invariant sETHAddressZeroHasNoBalance
use invariant sETHSolvencyCorrollary