##ETH

###ETH total

```solidity
    /// Total amount of ETH received by the contract
    function totalETHReceived() public view returns (uint256) { return address(this).balance + totalClaimed; }

    /// Total amount of ETH drawn down by syndicate beneficiaries regardless of SLOT type
    uint256 public totalClaimed;

    /// Amount of ETH claimed by user from sETH staking
    mapping(blsKey => mapping(address => uint256)) public sETHUserClaimForKnot;

    /// this is the amount that is separately allocated to either free floating or collateralized SLOT holders
    function calculateETHForFreeFloatingOrCollateralizedHolders() public view returns (uint256)
```

###ETH free floating shares

```solidity
    /// Total accrued ETH per free floating share for new and old stakers
    uint256 public accumulatedETHPerFreeFloatingShare;

    /// Last cached highest seen balance for all free floating shares
    uint256 public lastSeenETHPerFreeFloating;

    /// Once a BLS public key is no longer part of the syndicate, the accumulated ETH
    /// per free floating SLOT share is snapshotted so historical earnings can be drawn down correctly
    mapping(blsKey => uint256) public lastAccumulatedETHPerFreeFloatingShare;

    /// Calculate the amount of unclaimed ETH for a given BLS publice key
    /// + free floating SLOT staker without factoring in unprocessed rewards
   function calculateUnclaimedFreeFloatingETHShare(blsKey _blsPubKey, address _user) public view returns (uint256)

    /// Calculate the total unclaimed ETH across an array of BLS public keys for a free floating staker
    function batchPreviewUnclaimedETHAsFreeFloatingStaker(address _staker, blsKey[] calldata _blsPubKeys) external view returns (uint256)

    /// Preview the amount of unclaimed ETH available for an sETH staker against a KNOT which factors in unprocessed
    /// rewards from new ETH sent to contract
    /// @param _blsPubKey BLS public key of the KNOT that is registered with the syndicate
    /// @param _staker The address of a user that has staked sETH against the BLS public key
    function previewUnclaimedETHAsFreeFloatingStaker(address _staker,blsKey _blsPubKey) public view returns (uint256)

    /// Amount of ETH per free floating share that hasn't yet been allocated to each share
    function getUnprocessedETHForAllFreeFloatingSlot() public view returns (uint256)

    /// New accumulated ETH per free floating share that hasn't yet been applied
    /// @dev The return value is scaled by 1e24
    function calculateNewAccumulatedETHPerFreeFloatingShare() public view returns (uint256)
```

###ETH collateralized SLOT holders

```solidity
    /// Total accrued ETH for all collateralized SLOT holders per knot which
    /// is then distributed based on individual balances
    uint256 public accumulatedETHPerCollateralizedSlotPerKnot;

    /// Last cached highest seen balance for all collateralized shares
    uint256 public lastSeenETHPerCollateralizedSlotPerKnot;

    /// Total amount of ETH that has been allocated to the collateralized SLOT owners of a KNOT
    mapping(blsKey => uint256) public totalETHProcessedPerCollateralizedKnot;

    /// Total amount of ETH accrued for the collateralized SLOT owner of a KNOT
    mapping(blsKey => mapping(address => uint256)) public accruedEarningPerCollateralizedSlotOwnerOfKnot;

    /// Total amount of ETH claimed by the collateralized SLOT owner of a KNOT
    mapping(blsKey => mapping(address => uint256)) public claimedPerCollateralizedSlotOwnerOfKnot;

    /// Calculate the total unclaimed ETH across an array of BLS public keys for a collateralized SLOT staker
    function batchPreviewUnclaimedETHAsCollateralizedSlotOwner(address _staker,blsKey[] calldata _blsPubKeys) external view returns (uint256) {

    /// Preview the amount of unclaimed ETH available for a collatearlized SLOT staker against a KNOT
    /// which factors in unprocessed rewards from new ETH sent to contract
    /// @param _staker Address of a collateralized SLOT owner for a KNOT
    /// @param _blsPubKey BLS public key of the KNOT that is registered with the syndicate
    function previewUnclaimedETHAsCollateralizedSlotOwner(address _staker,blsKey _blsPubKey) public view returns (uint256)

    /// Amount of ETH per collateralized share that hasn't yet been allocated to each share
    function getUnprocessedETHForAllCollateralizedSlot() public view returns (uint256)

    /// New accumulated ETH per collateralized share per knot that hasn't yet been applied
    function calculateNewAccumulatedETHPerCollateralizedSharePerKnot() public view returns (uint256)
```

### sETH

```solidity
    /// Total number of sETH token shares staked across all houses
    uint256 public totalFreeFloatingShares;

    /// Total amount of free floating sETH staked
    mapping(blsKey => uint256) public sETHTotalStakeForKnot;

    /// Amount of sETH staked by user against a knot
    mapping(blsKey => mapping(address => uint256)) public sETHStakedBalanceForKnot;
```

### others

```solidity
    /// Block number after which if there are sETH staking slots available
    /// it can be supplied by anyone on the market
    uint256 public priorityStakingEndBlock;

    /// Number of knots registered with the syndicate which can be across any house
    uint256 public numberOfRegisteredKnots;

    /// Syndicate deployer can highlight addresses that get priority for staking
    /// free floating house sETH up to a certain block before anyone can do it
    mapping(address => bool) public isPriorityStaker;

    /// Informational - is the knot registered to this syndicate or not
    /// the node should point to this contract
    mapping(blsKey => bool) public isKnotRegistered;

    /// Whether a BLS public key, that has been previously registered, is no longer part
    /// of the syndicate and its shares (free floating or SLOT) cannot earn any more rewards
    mapping(blsKey => bool) public isNoLongerPartOfSyndicate;
```
