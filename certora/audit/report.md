bug1.patch : sETH.transfer return not tested

sETH invariant

total = somme all

```solidity
    /// @notice Total number of sETH token shares staked across all houses
    uint256 public totalFreeFloatingShares;

    /// @notice Total amount of free floating sETH staked
    mapping(bytes => uint256) public sETHTotalStakeForKnot;

    /// @notice Amount of sETH staked by user against a knot
    mapping(bytes => mapping(address => uint256)) public sETHStakedBalanceForKnot;

    /// @notice Amount of ETH claimed by user from sETH staking
    mapping(bytes => mapping(address => uint256)) public sETHUserClaimForKnot;
```

```solidity
    function stake(bytes[] calldata _blsPubKeys, uint256[] calldata _sETHAmounts, address _onBehalfOf) external {
        ...
        for (uint256 i; i < numOfKeys; ++i) {
            ...
            uint256 _sETHAmount = _sETHAmounts[i];
            uint256 totalStaked = sETHTotalStakeForKnot[_blsPubKey];
            ...
            totalFreeFloatingShares += _sETHAmount;
            sETHTotalStakeForKnot[_blsPubKey] += _sETHAmount;
            sETHStakedBalanceForKnot[_blsPubKey][_onBehalfOf] += _sETHAmount;
            sETHUserClaimForKnot[_blsPubKey][_onBehalfOf] +=
                (_sETHAmount * accumulatedETHPerFreeFloatingShare) / PRECISION;
            ...
            bool transferResult = sETH.transferFrom(msg.sender, address(this), _sETHAmount);
            if (!transferResult) revert UnableToStakeFreeFloatingSlot();
            ...
        }
    }
```

```solidity
    function unstake(
        address _unclaimedETHRecipient,
        address _sETHRecipient,
        bytes[] calldata _blsPubKeys,
        uint256[] calldata _sETHAmounts
    ) external nonReentrant {
        ...
        for (uint256 i; i < numOfKeys; ++i) {
            ...
            uint256 _sETHAmount = _sETHAmounts[i];
            ...
            if (!isNoLongerPartOfSyndicate[_blsPubKey]) {
                totalFreeFloatingShares -= _sETHAmount;
            }

            sETHTotalStakeForKnot[_blsPubKey] -= _sETHAmount;
            sETHStakedBalanceForKnot[_blsPubKey][msg.sender] -= _sETHAmount;

           uint256 accumulatedETHPerShare = _getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(_blsPubKey);
            sETHUserClaimForKnot[_blsPubKey][msg.sender] =
                (accumulatedETHPerShare * sETHStakedBalanceForKnot[_blsPubKey][msg.sender]) / PRECISION;

            bool transferResult = sETH.transfer(_sETHRecipient, _sETHAmount);
            if (!transferResult) revert TransferFailed();
            ...
        }
    }
```

```solidity
    function _deRegisterKnot(bytes memory _blsPublicKey) internal {
        ...
        totalFreeFloatingShares -= sETHTotalStakeForKnot[_blsPublicKey];
        ...
    }
```

```solidity
    function _claimAsStaker(address _recipient, bytes[] calldata _blsPubKeys) internal {
        ...
        totalClaimed += unclaimedUserShare;

        uint256 accumulatedETHPerShare =
            _getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(_blsPubKey);

        sETHUserClaimForKnot[_blsPubKey][msg.sender] =
        (accumulatedETHPerShare * sETHStakedBalanceForKnot[_blsPubKey][msg.sender]) / PRECISION;

        totalToTransfer += unclaimedUserShare;
        ...
    }
```

```solidity

```


div par zero => 2 rules
+ some in internal function not used !
+ maybe 1 other one or 2(search " / ")
