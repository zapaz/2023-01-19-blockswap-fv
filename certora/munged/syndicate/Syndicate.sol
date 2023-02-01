pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { StakehouseAPI } from "../../harnesses/SimplifiedStakehouseAPI.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
import { ReentrancyGuard } from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import { ISyndicateInit } from "../interfaces/ISyndicateInit.sol";
import { ETHTransferHelper } from "../transfer/ETHTransferHelper.sol";
import {
    ZeroAddress,
    EmptyArray,
    InconsistentArrayLengths,
    InvalidBLSPubKey,
    InvalidNumberOfCollateralizedOwners,
    KnotSlashed,
    FreeFloatingStakeAmountTooSmall,
    KnotIsNotRegisteredWithSyndicate,
    NotPriorityStaker,
    KnotIsFullyStakedWithFreeFloatingSlotTokens,
    InvalidStakeAmount,
    KnotIsNotAssociatedWithAStakeHouse,
    UnableToStakeFreeFloatingSlot,
    NothingStaked,
    TransferFailed,
    NotCollateralizedOwnerAtIndex,
    InactiveKnot,
    DuplicateArrayElements,
    KnotIsAlreadyRegistered,
    KnotHasAlreadyBeenDeRegistered
} from "./SyndicateErrors.sol";

/// @notice Syndicate registry and funds splitter for EIP1559 execution layer transaction tips across SLOT shares
/// @dev This contract can be extended to allow lending and borrowing of time slots for borrower to redeem any revenue generated within the specified window
contract Syndicate is ISyndicateInit, Initializable, Ownable, ReentrancyGuard, StakehouseAPI, ETHTransferHelper {

    /// @notice Emitted when the contract is initially deployed
    event ContractDeployed();

    /// @notice Emitted when accrued ETH per SLOT share type is updated
    event UpdateAccruedETH(uint256 unprocessed);

    /// @notice Emitted when new collateralized SLOT owners for a knot prompts re-calibration
    event CollateralizedSLOTReCalibrated(blsKey BLSPubKey);

    /// @notice Emitted when a new KNOT is associated with the syndicate contract
    event KNOTRegistered(blsKey BLSPubKey);

    /// @notice Emitted when a KNOT is de-registered from the syndicate
    event KnotDeRegistered(blsKey BLSPubKey);

    /// @notice Emitted when a priority staker is added to the syndicate
    event PriorityStakerRegistered(address indexed staker);

    /// @notice Emitted when a user stakes free floating sETH tokens
    event Staked(blsKey BLSPubKey, uint256 amount);

    /// @notice Emitted when a user unstakes free floating sETH tokens
    event UnStaked(blsKey BLSPubKey, uint256 amount);

    /// @notice Emitted when either an sETH staker or collateralized SLOT owner claims ETH
    event ETHClaimed(blsKey BLSPubKey, address indexed user, address recipient, uint256 claim, bool indexed isCollateralizedClaim);

    /// @notice Precision used in rewards calculations for scaling up and down
    uint256 public constant PRECISION = 1e24;

    /// @notice Total accrued ETH per free floating share for new and old stakers
    uint256 public accumulatedETHPerFreeFloatingShare;

    /// @notice Total accrued ETH for all collateralized SLOT holders per knot which is then distributed based on individual balances
    uint256 public accumulatedETHPerCollateralizedSlotPerKnot;

    /// @notice Last cached highest seen balance for all collateralized shares
    uint256 public lastSeenETHPerCollateralizedSlotPerKnot;

    /// @notice Last cached highest seen balance for all free floating shares
    uint256 public lastSeenETHPerFreeFloating;

    /// @notice Total number of sETH token shares staked across all houses
    uint256 public totalFreeFloatingShares;

    /// @notice Total amount of ETH drawn down by syndicate beneficiaries regardless of SLOT type
    uint256 public totalClaimed;

    /// @notice Number of knots registered with the syndicate which can be across any house
    uint256 public numberOfRegisteredKnots;

    /// @notice Informational - is the knot registered to this syndicate or not - the node should point to this contract
    mapping(blsKey => bool) public isKnotRegistered;

    /// @notice Block number after which if there are sETH staking slots available, it can be supplied by anyone on the market
    uint256 public priorityStakingEndBlock;

    /// @notice Syndicate deployer can highlight addresses that get priority for staking free floating house sETH up to a certain block before anyone can do it
    mapping(address => bool) public isPriorityStaker;

    /// @notice Total amount of free floating sETH staked
    mapping(blsKey => uint256) public sETHTotalStakeForKnot;

    /// @notice Amount of sETH staked by user against a knot
    mapping(blsKey => mapping(address => uint256)) public sETHStakedBalanceForKnot;

    /// @notice Amount of ETH claimed by user from sETH staking
    mapping(blsKey => mapping(address => uint256)) public sETHUserClaimForKnot;

    /// @notice Total amount of ETH that has been allocated to the collateralized SLOT owners of a KNOT
    mapping(blsKey => uint256) public totalETHProcessedPerCollateralizedKnot;

    /// @notice Total amount of ETH accrued for the collateralized SLOT owner of a KNOT
    mapping(blsKey => mapping(address => uint256)) public accruedEarningPerCollateralizedSlotOwnerOfKnot;

    /// @notice Total amount of ETH claimed by the collateralized SLOT owner of a KNOT
    mapping(blsKey => mapping(address => uint256)) public claimedPerCollateralizedSlotOwnerOfKnot;

    /// @notice Whether a BLS public key, that has been previously registered, is no longer part of the syndicate and its shares (free floating or SLOT) cannot earn any more rewards
    mapping(blsKey => bool) public isNoLongerPartOfSyndicate;

    /// @notice Once a BLS public key is no longer part of the syndicate, the accumulated ETH per free floating SLOT share is snapshotted so historical earnings can be drawn down correctly
    mapping(blsKey => uint256) public lastAccumulatedETHPerFreeFloatingShare;


    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() initializer {}

    /// @param _contractOwner Ethereum public key that will receive management rights of the contract
    /// @param _priorityStakingEndBlock Block number when priority sETH staking ends and anyone can stake
    /// @param _priorityStakers Optional list of addresses that will have priority for staking sETH against each knot registered
    /// @param _blsPubKeysForSyndicateKnots List of BLS public keys of Stakehouse protocol registered KNOTs participating in syndicate
    function initialize(
        address _contractOwner,
        uint256 _priorityStakingEndBlock,
        address[] memory _priorityStakers,
        blsKey[] memory _blsPubKeysForSyndicateKnots
    ) public virtual override initializer { // MUNGED internal => public
        _initialize(
            _contractOwner,
            _priorityStakingEndBlock,
            _priorityStakers,
            _blsPubKeysForSyndicateKnots
        );
    }

    /// @notice Allows the contract owner to append to the list of knots that are part of the syndicate
    /// @param _newBLSPublicKeyBeingRegistered List of BLS public keys being added to the syndicate
    function registerKnotsToSyndicate(
        blsKey[] memory _newBLSPublicKeyBeingRegistered
    ) public onlyOwner { // MUNGED internal => public
        // update accrued ETH per SLOT type
        updateAccruedETHPerShares();
        _registerKnotsToSyndicate(_newBLSPublicKeyBeingRegistered);
    }

    /// @notice Make knot shares of a registered list of BLS public keys inactive - the action cannot be undone and no further ETH accrued
    function deRegisterKnots(blsKey[] memory _blsPublicKeys) public onlyOwner {// MUNGED internal => public
        updateAccruedETHPerShares();
        _deRegisterKnots(_blsPublicKeys);
    }

    /// @notice Allows the contract owner to append to the list of priority sETH stakers
    /// @param _priorityStakers List of staker addresses eligible for sETH staking
    function addPriorityStakers(address[] memory _priorityStakers) public onlyOwner { // MUNGED internal => public
        updateAccruedETHPerShares();
        _addPriorityStakers(_priorityStakers);
    }

    /// @notice Should this block be in the future, it means only those listed in the priority staker list can stake sETH
    /// @param _endBlock Arbitrary block number after which anyone can stake up to 4 SLOT in sETH per KNOT
    function updatePriorityStakingBlock(uint256 _endBlock) public onlyOwner { // MUNGED internal => public
        updateAccruedETHPerShares();
        priorityStakingEndBlock = _endBlock;
    }

    /// @notice Update accrued ETH per SLOT share without distributing ETH as users of the syndicate individually pull funds
    function updateAccruedETHPerShares() public {
        // Ensure there are registered KNOTs. Syndicates are deployed with at least 1 registered but this can fall to zero.
        // Fee recipient should be re-assigned in the event that happens as any further ETH can be collected by owner
        if (numberOfRegisteredKnots > 0) {
            // All time, total ETH that was earned per slot type (free floating or collateralized)
            uint256 totalEthPerSlotType = calculateETHForFreeFloatingOrCollateralizedHolders();

            // Process free floating if there are staked shares
            uint256 freeFloatingUnprocessed;
            if (totalFreeFloatingShares > 0) {
                freeFloatingUnprocessed = getUnprocessedETHForAllFreeFloatingSlot();  // == totalEthPerSlotType - lastSeenETHPerFreeFloating
                accumulatedETHPerFreeFloatingShare += _calculateNewAccumulatedETHPerFreeFloatingShare(freeFloatingUnprocessed); // == accumulatedETHPerFreeFloatingShare + freeFloatingUnprocessed / totalFreeFloatingShares
                lastSeenETHPerFreeFloating = totalEthPerSlotType;
            }

            uint256 collateralizedUnprocessed = ((totalEthPerSlotType - lastSeenETHPerCollateralizedSlotPerKnot) / numberOfRegisteredKnots);
            accumulatedETHPerCollateralizedSlotPerKnot += collateralizedUnprocessed;
            lastSeenETHPerCollateralizedSlotPerKnot = totalEthPerSlotType;

            emit UpdateAccruedETH(freeFloatingUnprocessed + collateralizedUnprocessed);
        }
    }

    /// @notice Stake up to 4 collateralized SLOT worth of sETH per KNOT to get a portion of syndicate rewards
    /// @param _blsPubKeys List of BLS public keys for KNOTs registered with the syndicate
    /// @param _sETHAmounts Per BLS public key, the total amount of sETH that will be staked (up to 4 collateralized SLOT per KNOT)
    /// @param _onBehalfOf Allows a caller to specify an address that will be assigned stake ownership and rights to claim
    function stake(blsKey[] memory _blsPubKeys, uint256[] memory _sETHAmounts, address _onBehalfOf) public { // MUNGED bytes => blsKey calldata => memory & external => public
        uint256 numOfKeys = _blsPubKeys.length;
        if (numOfKeys == 0) revert EmptyArray();
        if (numOfKeys != _sETHAmounts.length) revert InconsistentArrayLengths();
        if (_onBehalfOf == address(0)) revert ZeroAddress();

        // Make sure we have the latest accrued information
        updateAccruedETHPerShares();

        for (uint256 i; i < numOfKeys; ++i) {
            blsKey _blsPubKey = _blsPubKeys[i];
            uint256 _sETHAmount = _sETHAmounts[i];

            if (_sETHAmount < 1 gwei) revert FreeFloatingStakeAmountTooSmall();
            if (!isKnotRegistered[_blsPubKey] || isNoLongerPartOfSyndicate[_blsPubKey]) revert KnotIsNotRegisteredWithSyndicate();

            if (block.number < priorityStakingEndBlock && !isPriorityStaker[_onBehalfOf]) revert NotPriorityStaker();

            uint256 totalStaked = sETHTotalStakeForKnot[_blsPubKey];
            if (totalStaked == 12 ether) revert KnotIsFullyStakedWithFreeFloatingSlotTokens();

            if (_sETHAmount + totalStaked > 12 ether) revert InvalidStakeAmount();

            totalFreeFloatingShares += _sETHAmount;
            sETHTotalStakeForKnot[_blsPubKey] += _sETHAmount;
            sETHStakedBalanceForKnot[_blsPubKey][_onBehalfOf] += _sETHAmount;
            sETHUserClaimForKnot[_blsPubKey][_onBehalfOf] += (_sETHAmount * accumulatedETHPerFreeFloatingShare) / PRECISION;

            (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(_blsPubKey));
            if (stakeHouse == address(0)) revert KnotIsNotAssociatedWithAStakeHouse();
            IERC20 sETH = IERC20(getSlotRegistry().stakeHouseShareTokens(stakeHouse));
            bool transferResult = sETH.transferFrom(msg.sender, address(this), _sETHAmount);
            if (!transferResult) revert UnableToStakeFreeFloatingSlot();

            emit Staked(_blsPubKey, _sETHAmount);
        }
    }

    /// @notice Unstake an sETH position against a particular KNOT and claim ETH on exit
    /// @param _unclaimedETHRecipient The address that will receive any unclaimed ETH received to the syndicate
    /// @param _sETHRecipient The address that will receive the sETH that is being unstaked
    /// @param _blsPubKeys List of BLS public keys for KNOTs registered with the syndicate
    /// @param _sETHAmounts Per BLS public key, the total amount of sETH that will be unstaked
    function unstake(
        address _unclaimedETHRecipient,
        address _sETHRecipient,
        blsKey[] memory _blsPubKeys, // MUNGED bytes => blsKey & calldata => memory
        uint256[] memory _sETHAmounts // MUNGED calldata => memory
    ) public nonReentrant { // MUNGED external => public
        uint256 numOfKeys = _blsPubKeys.length;
        if (numOfKeys == 0) revert EmptyArray();
        if (numOfKeys != _sETHAmounts.length) revert InconsistentArrayLengths();
        if (_unclaimedETHRecipient == address(0)) revert ZeroAddress();
        if (_sETHRecipient == address(0)) revert ZeroAddress();

        // Claim all ETH owed before unstaking but even if nothing is owed `updateAccruedETHPerShares` will be called
        _claimAsStaker(_unclaimedETHRecipient, _blsPubKeys);

        for (uint256 i; i < numOfKeys; ++i) {
            blsKey _blsPubKey = _blsPubKeys[i];
            uint256 _sETHAmount = _sETHAmounts[i];
            if (sETHStakedBalanceForKnot[_blsPubKey][msg.sender] < _sETHAmount) revert NothingStaked();

            (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(_blsPubKey));
            IERC20 sETH = IERC20(getSlotRegistry().stakeHouseShareTokens(stakeHouse));

            // Only decrease totalFreeFloatingShares in the event that the knot is still active in the syndicate
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

            emit UnStaked(_blsPubKey, _sETHAmount);
        }
    }

    /// @notice Claim ETH cashflow from the syndicate as an sETH staker proportional to how much the user has staked
    /// @param _recipient Address that will receive the share of ETH funds
    /// @param _blsPubKeys List of BLS public keys that the caller has staked against
    function claimAsStaker(address _recipient, blsKey[] memory _blsPubKeys) public nonReentrant {
        _claimAsStaker(_recipient, _blsPubKeys);
    }

    /// @param _blsPubKeys List of BLS public keys that the caller has staked against
    function claimAsCollateralizedSLOTOwner(
        address _recipient,
        blsKey[] memory _blsPubKeys // MUNGED bytes[] => blsKey[] & calldata => memory
    ) public nonReentrant { // MUNGED external => public
        uint256 numOfKeys = _blsPubKeys.length;
        if (numOfKeys == 0) revert EmptyArray();
        if (_recipient == address(0)) revert ZeroAddress();
        if (_recipient == address(this)) revert ZeroAddress();

        // Make sure we have the latest accrued information for all shares
        updateAccruedETHPerShares();

        uint256 totalToTransfer;
        for (uint256 i; i < numOfKeys; ++i) {
            blsKey _blsPubKey = _blsPubKeys[i];
            if (!isKnotRegistered[_blsPubKey]) revert KnotIsNotRegisteredWithSyndicate();

            // process newly accrued ETH and distribute it to collateralized SLOT owners for the given knot
            _updateCollateralizedSlotOwnersLiabilitySnapshot(_blsPubKey);

            // Calculate total amount of unclaimed ETH
            uint256 userShare = accruedEarningPerCollateralizedSlotOwnerOfKnot[_blsPubKey][msg.sender];

            // This is designed to cope with falling SLOT balances i.e. when collateralized SLOT is burnt after applying penalties
            uint256 unclaimedUserShare = userShare - claimedPerCollateralizedSlotOwnerOfKnot[_blsPubKey][msg.sender];

            // Send ETH to the user if there is an unclaimed amount
            if (unclaimedUserShare > 0) {
                // Increase total claimed and claimed at the user level
                totalClaimed += unclaimedUserShare;
                claimedPerCollateralizedSlotOwnerOfKnot[_blsPubKey][msg.sender] = userShare;

                // Send ETH to user
                totalToTransfer += unclaimedUserShare;

                emit ETHClaimed(
                    _blsPubKey,
                    msg.sender,
                    _recipient,
                    unclaimedUserShare,
                    true
                );
            }
        }

        _transferETH(_recipient, totalToTransfer);
    }

    /// @notice For any new ETH received by the syndicate, at the knot level allocate ETH owed to each collateralized owner
    /// @param _blsPubKey BLS public key relating to the collateralized owners that need updating
    function updateCollateralizedSlotOwnersAccruedETH(blsKey _blsPubKey) public { // MUNGED internal => public
        _updateCollateralizedSlotOwnersLiabilitySnapshot(_blsPubKey);
    }

    /// @notice For any new ETH received by the syndicate, at the knot level allocate ETH owed to each collateralized owner and do it for a batch of knots
    /// @param _blsPubKeys List of BLS public keys related to the collateralized owners that need updating
    function batchUpdateCollateralizedSlotOwnersAccruedETH(blsKey[] memory _blsPubKeys) public { // MUNGED internal => public
        uint256 numOfKeys = _blsPubKeys.length;
        if (numOfKeys == 0) revert EmptyArray();
        for (uint256 i; i < numOfKeys; ++i) {
            _updateCollateralizedSlotOwnersLiabilitySnapshot(_blsPubKeys[i]);
        }
    }

    /// @notice Syndicate contract can receive ETH
    receive() external payable {
        // No logic here because one cannot assume that more than 21K GAS limit is forwarded
    }

    /// @notice Calculate the amount of unclaimed ETH for a given BLS publice key + free floating SLOT staker without factoring in unprocessed rewards
    /// @param _blsPubKey BLS public key of the KNOT that is registered with the syndicate
    /// @param _user The address of a user that has staked sETH against the BLS public key
    function calculateUnclaimedFreeFloatingETHShare(blsKey _blsPubKey, address _user) public view returns (uint256) {
        // Check the user has staked sETH for the KNOT
        uint256 stakedBal = sETHStakedBalanceForKnot[_blsPubKey][_user];
        if (stakedBal < 1 gwei) return 0;

        // Get the amount of ETH eligible for the user based on their staking amount
        uint256 accumulatedETHPerShare = _getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(_blsPubKey);
        uint256 userShare = (accumulatedETHPerShare * stakedBal) / PRECISION;

        // Calculate how much their unclaimed share of ETH is based on total ETH claimed so far
        return userShare - sETHUserClaimForKnot[_blsPubKey][_user];
    }

    /// @notice Using `highestSeenBalance`, this is the amount that is separately allocated to either free floating or collateralized SLOT holders
    function calculateETHForFreeFloatingOrCollateralizedHolders() public view returns (uint256) {
        // Get total amount of ETH that can be drawn down by all SLOT holders associated with a knot
        uint256 ethPerKnot = totalETHReceived();

        // Get the amount of ETH eligible for free floating sETH or collateralized SLOT stakers
        return ethPerKnot / 2;
    }

    /// @notice Calculate the total unclaimed ETH across an array of BLS public keys for a free floating staker
    function batchPreviewUnclaimedETHAsFreeFloatingStaker(
        address _staker,
        blsKey[] calldata _blsPubKeys
    ) external view returns (uint256) {
        uint256 accumulated;
        uint256 numOfKeys = _blsPubKeys.length;
        for (uint256 i; i < numOfKeys; ++i) {
            accumulated += previewUnclaimedETHAsFreeFloatingStaker(_staker, _blsPubKeys[i]);
        }

        return accumulated;
    }

    /// @notice Preview the amount of unclaimed ETH available for an sETH staker against a KNOT which factors in unprocessed rewards from new ETH sent to contract
    /// @param _blsPubKey BLS public key of the KNOT that is registered with the syndicate
    /// @param _staker The address of a user that has staked sETH against the BLS public key
    function previewUnclaimedETHAsFreeFloatingStaker(
        address _staker,
        blsKey _blsPubKey
    ) public view returns (uint256) {
        uint256 currentAccumulatedETHPerFreeFloatingShare = accumulatedETHPerFreeFloatingShare;
        uint256 updatedAccumulatedETHPerFreeFloatingShare =
                            currentAccumulatedETHPerFreeFloatingShare + calculateNewAccumulatedETHPerFreeFloatingShare();

        uint256 stakedBal = sETHStakedBalanceForKnot[_blsPubKey][_staker];
        uint256 userShare = (updatedAccumulatedETHPerFreeFloatingShare * stakedBal) / PRECISION;

        return userShare - sETHUserClaimForKnot[_blsPubKey][_staker];
    }

    /// @notice Calculate the total unclaimed ETH across an array of BLS public keys for a collateralized SLOT staker
    function batchPreviewUnclaimedETHAsCollateralizedSlotOwner(
        address _staker,
        blsKey[] calldata _blsPubKeys
    ) external view returns (uint256) {
        uint256 accumulated;
        uint256 numOfKeys = _blsPubKeys.length;
        for (uint256 i; i < numOfKeys; ++i) {
            accumulated += previewUnclaimedETHAsCollateralizedSlotOwner(_staker, _blsPubKeys[i]);
        }

        return accumulated;
    }

    /// @notice Preview the amount of unclaimed ETH available for a collatearlized SLOT staker against a KNOT which factors in unprocessed rewards from new ETH sent to contract
    /// @param _staker Address of a collateralized SLOT owner for a KNOT
    /// @param _blsPubKey BLS public key of the KNOT that is registered with the syndicate
    function previewUnclaimedETHAsCollateralizedSlotOwner(
        address _staker,
        blsKey _blsPubKey
    ) public view returns (uint256) {
        // Per collateralized SLOT per KNOT before distributing to individual collateralized owners
        uint256 accumulatedSoFar = accumulatedETHPerCollateralizedSlotPerKnot
                    + ((calculateETHForFreeFloatingOrCollateralizedHolders() - lastSeenETHPerCollateralizedSlotPerKnot) / numberOfRegisteredKnots);

        uint256 unprocessedForKnot = accumulatedSoFar - totalETHProcessedPerCollateralizedKnot[_blsPubKey];

        // Fetch information on what has been processed so far against the ECDSA address of the collateralized SLOT owner
        uint256 currentAccrued = accruedEarningPerCollateralizedSlotOwnerOfKnot[_blsPubKey][_staker];

        // Fetch information about the knot including total slashed amount
        uint256 currentSlashedAmount = getSlotRegistry().currentSlashedAmountOfSLOTForKnot(blsKey.unwrap(_blsPubKey));
        uint256 numberOfCollateralisedSlotOwnersForKnot = getSlotRegistry().numberOfCollateralisedSlotOwnersForKnot(blsKey.unwrap(_blsPubKey));
        (address stakeHouse,,,,,) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(_blsPubKey));

        // Find the collateralized SLOT owner and work out how much they're owed
        for (uint256 i; i < numberOfCollateralisedSlotOwnersForKnot; ++i) {
            address collateralizedOwnerAtIndex = getSlotRegistry().getCollateralisedOwnerAtIndex(blsKey.unwrap(_blsPubKey), i);
            if (collateralizedOwnerAtIndex == _staker) {
                uint256 balance = getSlotRegistry().totalUserCollateralisedSLOTBalanceForKnot(
                    stakeHouse,
                    collateralizedOwnerAtIndex,
                    blsKey.unwrap(_blsPubKey)
                );

                if (currentSlashedAmount < 4 ether) {
                    currentAccrued +=
                    numberOfCollateralisedSlotOwnersForKnot > 1 ? balance * unprocessedForKnot / (4 ether - currentSlashedAmount)
                    : unprocessedForKnot;
                }
                break;
            }
        }

        return currentAccrued - claimedPerCollateralizedSlotOwnerOfKnot[_blsPubKey][_staker];
    }

    /// @notice Amount of ETH per free floating share that hasn't yet been allocated to each share
    function getUnprocessedETHForAllFreeFloatingSlot() public view returns (uint256) {
        return calculateETHForFreeFloatingOrCollateralizedHolders() - lastSeenETHPerFreeFloating;
    }

    /// @notice Amount of ETH per collateralized share that hasn't yet been allocated to each share
    function getUnprocessedETHForAllCollateralizedSlot() public view returns (uint256) {
        return ((calculateETHForFreeFloatingOrCollateralizedHolders() - lastSeenETHPerCollateralizedSlotPerKnot) / numberOfRegisteredKnots);
    }

    /// @notice New accumulated ETH per free floating share that hasn't yet been applied
    /// @dev The return value is scaled by 1e24
    function calculateNewAccumulatedETHPerFreeFloatingShare() public view returns (uint256) {
        uint256 ethSinceLastUpdate = getUnprocessedETHForAllFreeFloatingSlot();
        return _calculateNewAccumulatedETHPerFreeFloatingShare(ethSinceLastUpdate);
    }

    /// @notice New accumulated ETH per collateralized share per knot that hasn't yet been applied
    function calculateNewAccumulatedETHPerCollateralizedSharePerKnot() public view returns (uint256) {
        uint256 ethSinceLastUpdate = getUnprocessedETHForAllCollateralizedSlot();
        return accumulatedETHPerCollateralizedSlotPerKnot + ethSinceLastUpdate;
    }

    /// @notice Total amount of ETH received by the contract
    function totalETHReceived() public view returns (uint256) {
        return address(this).balance + totalClaimed;
    }

    /// @dev Internal logic for initializing the syndicate contract
    function _initialize(
        address _contractOwner,
        uint256 _priorityStakingEndBlock,
        address[] memory _priorityStakers,
        blsKey[] memory _blsPubKeysForSyndicateKnots
    ) internal {
        // Transfer ownership from the deployer to the address specified as the owner
        _transferOwnership(_contractOwner);

        // Add the initial set of knots to the syndicate
        _registerKnotsToSyndicate(_blsPubKeysForSyndicateKnots);

        // Optionally process priority staking if the required params and array is configured
        if (_priorityStakingEndBlock > block.number) {
            priorityStakingEndBlock = _priorityStakingEndBlock;
            _addPriorityStakers(_priorityStakers);
        }

        emit ContractDeployed();
    }

    /// Given an amount of ETH allocated to the collateralized SLOT owners of a KNOT, distribute this amongs the current set of collateralized owners (a dynamic set of addresses and balances)
    function _updateCollateralizedSlotOwnersLiabilitySnapshot(blsKey _blsPubKey) internal {
        // Establish how much new ETH is for the new KNOT
        uint256 unprocessedETHForCurrentKnot =
                    accumulatedETHPerCollateralizedSlotPerKnot - totalETHProcessedPerCollateralizedKnot[_blsPubKey];

        // Get information about the knot i.e. associated house and whether its active
        (address stakeHouse,,,,,bool isActive) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(_blsPubKey));

        // Assuming that there is unprocessed ETH and the knot is still part of the syndicate
        if (unprocessedETHForCurrentKnot > 0 && !isNoLongerPartOfSyndicate[_blsPubKey]) {
            uint256 currentSlashedAmount = getSlotRegistry().currentSlashedAmountOfSLOTForKnot(blsKey.unwrap(_blsPubKey));

            // Don't allocate ETH when the current slashed amount is four. Syndicate will wait until ETH is topped up to claim revenue
            if (currentSlashedAmount < 4 ether) {
                // This copes with increasing numbers of collateralized slot owners and also copes with SLOT that has been slashed but not topped up
                uint256 numberOfCollateralisedSlotOwnersForKnot = getSlotRegistry().numberOfCollateralisedSlotOwnersForKnot(blsKey.unwrap(_blsPubKey));

                if (numberOfCollateralisedSlotOwnersForKnot == 1) {
                    // For only 1 collateralized SLOT owner, they get the full amount of unprocessed ETH for the knot
                    address collateralizedOwnerAtIndex = getSlotRegistry().getCollateralisedOwnerAtIndex(blsKey.unwrap(_blsPubKey), 0);
                    accruedEarningPerCollateralizedSlotOwnerOfKnot[_blsPubKey][collateralizedOwnerAtIndex] += unprocessedETHForCurrentKnot;
                } else {
                    for (uint256 i; i < numberOfCollateralisedSlotOwnersForKnot; ++i) {
                        address collateralizedOwnerAtIndex = getSlotRegistry().getCollateralisedOwnerAtIndex(blsKey.unwrap(_blsPubKey), i);
                        uint256 balance = getSlotRegistry().totalUserCollateralisedSLOTBalanceForKnot(
                            stakeHouse,
                            collateralizedOwnerAtIndex,
                            blsKey.unwrap(_blsPubKey)
                        );

                        accruedEarningPerCollateralizedSlotOwnerOfKnot[_blsPubKey][collateralizedOwnerAtIndex] +=
                            balance * unprocessedETHForCurrentKnot / (4 ether - currentSlashedAmount);
                    }
                }

                // record so unprocessed goes to zero
                totalETHProcessedPerCollateralizedKnot[_blsPubKey] = accumulatedETHPerCollateralizedSlotPerKnot;
            }
        }

        // if the knot is no longer active, no further accrual of rewards are possible snapshots are possible but ETH accrued up to that point
        // Basically, under a rage quit or voluntary withdrawal from the beacon chain, the knot kick is auto-propagated to syndicate
        if (!isActive && !isNoLongerPartOfSyndicate[_blsPubKey]) {
            _deRegisterKnot(_blsPubKey);
        }
    }

    function _calculateCollateralizedETHOwedPerKnot() internal view returns (uint256) {
        uint256 collateralizedSLOTShareOfETH = calculateETHForFreeFloatingOrCollateralizedHolders();
        uint256 collateralizedSLOTShareOfETHPerKnot = (collateralizedSLOTShareOfETH / numberOfRegisteredKnots);
        return collateralizedSLOTShareOfETHPerKnot;
    }

    /// @dev Business logic for calculating per collateralized share how much ETH from 1559 rewards is owed
    function _calculateNewAccumulatedETHPerCollateralizedShare(uint256 _ethSinceLastUpdate) internal view returns (uint256) {
        return (_ethSinceLastUpdate * PRECISION) / (numberOfRegisteredKnots * 4 ether);
    }

    /// @dev Business logic for calculating per free floating share how much ETH from 1559 rewards is owed
    function _calculateNewAccumulatedETHPerFreeFloatingShare(uint256 _ethSinceLastUpdate) internal view returns (uint256) {
        return totalFreeFloatingShares > 0 ? (_ethSinceLastUpdate * PRECISION) / totalFreeFloatingShares : 0;
    }

    /// @dev Business logic for adding a new set of knots to the syndicate for collecting revenue
    function _registerKnotsToSyndicate(blsKey[] memory _blsPubKeysForSyndicateKnots) internal {
        uint256 knotsToRegister = _blsPubKeysForSyndicateKnots.length;
        if (knotsToRegister == 0) revert EmptyArray();
        numberOfRegisteredKnots += knotsToRegister;

        for (uint256 i; i < knotsToRegister; ++i) {
            blsKey blsPubKey = _blsPubKeysForSyndicateKnots[i];
            if (isKnotRegistered[blsPubKey]) revert KnotIsAlreadyRegistered();

            // incomming knot collateralized SLOT holders do not get historical earnings
            totalETHProcessedPerCollateralizedKnot[blsPubKey] = accumulatedETHPerCollateralizedSlotPerKnot;

            // Health check - if knot is inactive or slashed, should it really be part of the syndicate?
            // KNOTs closer to 32 effective at all times is the target
            (,,,,,bool isActive) = getStakeHouseUniverse().stakeHouseKnotInfo(blsKey.unwrap(blsPubKey));
            if (!isActive) revert InactiveKnot();

            uint256 numberOfCollateralisedSlotOwnersForKnot = getSlotRegistry().numberOfCollateralisedSlotOwnersForKnot(blsKey.unwrap(blsPubKey));
            if (numberOfCollateralisedSlotOwnersForKnot < 1) revert InvalidNumberOfCollateralizedOwners();
            if (getSlotRegistry().currentSlashedAmountOfSLOTForKnot(blsKey.unwrap(blsPubKey)) != 0) revert InvalidNumberOfCollateralizedOwners();

            isKnotRegistered[blsPubKey] = true;
            emit KNOTRegistered(blsPubKey);
        }
    }

    /// @dev Business logic for adding priority stakers to the syndicate
    function _addPriorityStakers(address[] memory _priorityStakers) internal {
        uint256 numOfStakers = _priorityStakers.length;
        if (numOfStakers == 0) revert EmptyArray();
        for (uint256 i; i < numOfStakers; ++i) {
            address staker = _priorityStakers[i];

            if (i > 0 && staker < _priorityStakers[i-1]) revert DuplicateArrayElements();

            isPriorityStaker[staker] = true;

            emit PriorityStakerRegistered(staker);
        }
    }

    /// @dev Business logic for de-registering a set of knots from the syndicate and doing the required snapshots to ensure historical earnings are preserved
    function _deRegisterKnots(blsKey[] memory _blsPublicKeys) internal {
        uint256 numOfKeys = _blsPublicKeys.length;
        for (uint256 i; i < numOfKeys; ++i) {
            blsKey blsPublicKey = _blsPublicKeys[i];

            // Do one final snapshot of ETH owed to the collateralized SLOT owners so they can claim later
            _updateCollateralizedSlotOwnersLiabilitySnapshot(blsPublicKey);

            // Execute the business logic for de-registering the single knot
            _deRegisterKnot(blsPublicKey);
        }
    }

    /// @dev Business logic for de-registering a specific knots assuming all accrued ETH has been processed
    function _deRegisterKnot(blsKey _blsPublicKey) internal {
        if (isKnotRegistered[_blsPublicKey] == false) revert KnotIsNotRegisteredWithSyndicate();
        if (isNoLongerPartOfSyndicate[_blsPublicKey] == true) revert KnotHasAlreadyBeenDeRegistered();

        // We flag that the knot is no longer part of the syndicate
        isNoLongerPartOfSyndicate[_blsPublicKey] = true;

        // For the free floating and collateralized SLOT of the knot, snapshot the accumulated ETH per share
        lastAccumulatedETHPerFreeFloatingShare[_blsPublicKey] = accumulatedETHPerFreeFloatingShare;

        // We need to reduce `totalFreeFloatingShares` in order to avoid further ETH accruing to shares of de-registered knot
        totalFreeFloatingShares -= sETHTotalStakeForKnot[_blsPublicKey];

        // Total number of registered knots with the syndicate reduces by one
        numberOfRegisteredKnots -= 1;

        emit KnotDeRegistered(_blsPublicKey);
    }

    /// @dev Work out the accumulated ETH per free floating share value that must be used for distributing ETH
    function _getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(
        blsKey _blsPublicKey
    ) internal view returns (uint256) {
        return
        lastAccumulatedETHPerFreeFloatingShare[_blsPublicKey] > 0 ?
        lastAccumulatedETHPerFreeFloatingShare[_blsPublicKey] :
        accumulatedETHPerFreeFloatingShare;
    }

    /// @dev Business logic for allowing a free floating SLOT holder to claim their share of ETH
    function _claimAsStaker(address _recipient, blsKey[] memory _blsPubKeys) internal {
        uint256 numOfKeys = _blsPubKeys.length;
        if (numOfKeys == 0) revert EmptyArray();
        if (_recipient == address(0)) revert ZeroAddress();
        if (_recipient == address(this)) revert ZeroAddress();

        // Make sure we have the latest accrued information
        updateAccruedETHPerShares();

        uint256 totalToTransfer;
        for (uint256 i; i < numOfKeys; ++i) {
            blsKey _blsPubKey = _blsPubKeys[i];
            if (!isKnotRegistered[_blsPubKey]) revert KnotIsNotRegisteredWithSyndicate();

            uint256 unclaimedUserShare = calculateUnclaimedFreeFloatingETHShare(_blsPubKey, msg.sender);

            // this means that user can call the funtion even if there is nothing to claim but the
            // worst that will happen is that they will just waste gas. this is needed for unstaking
            if (unclaimedUserShare > 0) {
                // Increase total claimed at the contract level
                totalClaimed += unclaimedUserShare;

                // Work out which accumulated ETH per free floating share value was used
                uint256 accumulatedETHPerShare = _getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(_blsPubKey);

                // Update the total ETH claimed by the free floating SLOT holder based on their share of sETH
                sETHUserClaimForKnot[_blsPubKey][msg.sender] =
                (accumulatedETHPerShare * sETHStakedBalanceForKnot[_blsPubKey][msg.sender]) / PRECISION;

                // Calculate how much ETH to send to the user
                totalToTransfer += unclaimedUserShare;

                emit ETHClaimed(
                    _blsPubKey,
                    msg.sender,
                    _recipient,
                    unclaimedUserShare,
                    false
                );
            }
        }

        _transferETH(_recipient, totalToTransfer);
    }
}