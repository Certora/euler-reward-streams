/* Rules for `StakingRewardStreams` */
using DummyERC20 as _ERC20;

methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    function rewardAmount(address, address, uint48) external returns (uint256) envfree;
    function totalRewardClaimed(address, address) external returns (uint256) envfree;
    function totalRewardRegistered(address, address) external returns (uint256) envfree;
    function getEpoch(uint48) external returns (uint48) envfree;
    
    function DummyERC20.balanceOf(address) external returns (uint256) envfree;

    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
}


/// @title Staking increases staked balance by given amount
rule stakeIntergrity(address rewarded, uint256 amount) {
    env e;
    require e.msg.sender != currentContract.evc;
    uint256 preBalance = balanceOf(e.msg.sender, rewarded);

    stake(e, rewarded, amount);

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);

    assert (
        amount != max_uint256 => to_mathint(postBalance) == preBalance + amount,
        "Staking increases staked balance by given amount"
    );
}


/// @title An example showing rewards can be given
rule canBeRewarded(address rewarded, address recipient, bool forfeitRecentReward) {
    uint256 preBalance = _ERC20.balanceOf(recipient);

    env e;
    claimReward(e, rewarded, _ERC20, recipient, forfeitRecentReward);

    uint256 postBalance = _ERC20.balanceOf(recipient);
    satisfy postBalance > preBalance;
}


/// @title Those that stake more should earn more rewards
rule stakeMoreEarnMore(
    address staker1,
    address staker2,
    address rewarded,
    address reward,
    bool forfeitRecentReward
) {
    env e1;
    env e2;
    
    // TODO: generalize the following two require statements
    require e1.msg.sender != currentContract.evc;
    require e2.msg.sender != currentContract.evc;

    uint256 earned1 = earnedReward(e1, staker1, rewarded, reward, forfeitRecentReward);
    uint256 earned2 = earnedReward(e2, staker1, rewarded, reward, forfeitRecentReward);

    require e2.block.timestamp > e1.block.timestamp;
    uint256 earned1Late = earnedReward(e1, staker1, rewarded, reward, forfeitRecentReward);
    uint256 earned2Late = earnedReward(e2, staker1, rewarded, reward, forfeitRecentReward);

    mathint diff1 = earned1Late - earned1;
    mathint diff2 = earned2Late - earned2;

    assert (
        balanceOf(staker1, rewarded) >= balanceOf(staker2, rewarded) => diff1 >= diff2,
        "stake more earn more"
    );
}


/// @title Staking and immediately unstaking should not yield profit
rule stakeUnStakeNoBonus(uint256 amount, address staker, bool forfeitRecentReward) {

    require amount < max_uint256;
    uint256 preBalance = _ERC20.balanceOf(staker);

    env e;
    require e.msg.sender == staker;
    require e.msg.sender != currentContract.evc;
    stake(e, _ERC20, amount);
    unstake(e, _ERC20, amount, staker, forfeitRecentReward);

    uint256 postBalance = _ERC20.balanceOf(staker);
    assert (
        postBalance <= preBalance,
        "staking and immediately unstaking should give no reward"
    );
}

/// @title Require rewards sum less than total registered and total registered not big
/// @notice This depends on `loop_iter` being at most 3
/// @notice Needed to prevent overflows and unsafe down-casting in `calculateRewards`
function sumRewardsNotTooBig(address rewarded, address reward, uint48 initialTime) {
    uint48 epoch1 = getEpoch(initialTime);
    uint48 epoch2 = require_uint48(epoch1 + 1);
    uint48 epoch3 = require_uint48(epoch1 + 2);

    requireInvariant rewardAmountLessThanTotal(rewarded, reward, epoch1);
    requireInvariant rewardSumLessThanTotal(rewarded, reward, epoch1, epoch2);
    requireInvariant rewardSum3LessThanTotal(rewarded, reward, epoch1, epoch2, epoch3);

    requireInvariant totalRegisteredIsNotBig(rewarded, reward);
    requireInvariant EpochDurationSizeLimit();
}

/*
/// @title Earned rewards are weakly monotonic increasing with time
rule earnedRewardsNonDecreasing(
    address account,
    address rewarded,
    address reward,
    bool forfeitRecentReward
) {
    require account != 0;  // Address zero is for virtually accrued
    uint48 lastUpdated = currentContract.distributions[rewarded][reward].lastUpdated;

    // Set up the environments
    env e1;
    env e2;

    require e1.block.timestamp < 2^32;  // Code rounds to `uint48`
    require e1.block.timestamp >= e2.block.timestamp;
    require e2.block.timestamp >= require_uint256(lastUpdated);

    // Require rewards sum less than total registered
    sumRewardsNotTooBig(rewarded, reward, lastUpdated);

    require (
        require_uint256(currentContract.distributions[rewarded][reward].accumulator) <=
        totalRewardRegistered(rewarded, reward)
    );

    uint256 earned1 = earnedReward(e1, account, rewarded, reward, forfeitRecentReward);
    uint256 earned2 = earnedReward(e2, account, rewarded, reward, forfeitRecentReward);

    assert (earned1 >= earned2, "earned rewards are non decreasing");
}
*/

/// @title Accumulator is non-decreasing
rule accumulatorIsNonDecreasing(method f, address rewarded, address reward) {
    // Require rewards sum less than total registered
    uint48 lastUpdated = currentContract.distributions[rewarded][reward].lastUpdated;
    sumRewardsNotTooBig(rewarded, reward, lastUpdated);

    // TODO: need to prove the following as an invariant!
    require (
        require_uint256(currentContract.distributions[rewarded][reward].accumulator) <=
        totalRewardRegistered(rewarded, reward)
    );

    uint208 preAccumulated = currentContract.distributions[rewarded][reward].accumulator;

    env e;
    calldataarg args;
    f(e, args);

    uint208 postAccumulated = currentContract.distributions[rewarded][reward].accumulator;
    assert (postAccumulated >= preAccumulated, "accumulator is non-decreasing");
}

// ---- Claimed and total reward -----------------------------------------------

/// @title Total claimed is non-decreasing
rule totalClaimedIsNonDecreasing(method f, address rewarded, address reward) {
    uint256 preClaimed = totalRewardClaimed(rewarded, reward);

    env e;
    calldataarg args;
    f(e, args);

    uint256 postClaimed = totalRewardClaimed(rewarded, reward);
    assert (postClaimed >= preClaimed, "total claimed is non-decreasing");
}


/// @title Staked balance is reduced only by calling `unstake`
rule stakedReduceProperty(method f, address account, address rewarded) {
    uint256 preBalance = balanceOf(account, rewarded);

    env e;
    calldataarg args;
    f(e, args);

    uint256 postBalance = balanceOf(account, rewarded);
    assert (
        postBalance < preBalance =>
        f.selector == sig:unstake(address, uint256, address, bool).selector,
        "staked reduced only by unstake"
    );
}

/*
invariant accumulatorLessThanTotal(address rewarded, address reward)
    (
        currentContract.distributions[rewarded][reward].accumulator <=
        totalRewardRegistered(rewarded, reward)
    );
*/

/// @title Reward amount per epoch is not greater than total registered reward
invariant rewardAmountLessThanTotal(address rewarded, address reward, uint48 epoch)
    rewardAmount(rewarded, reward, epoch) <= totalRewardRegistered(rewarded, reward);


/// @title The sum of rewards of two different epochs is not greater than total
/// registered reward
invariant rewardSumLessThanTotal(
    address rewarded, address reward, uint48 epoch1, uint48 epoch2
)
    epoch1 != epoch2 => (
        rewardAmount(rewarded, reward, epoch1) +
        rewardAmount(rewarded, reward, epoch2) <=
        to_mathint(totalRewardRegistered(rewarded, reward))
    );

invariant rewardSum3LessThanTotal(
    address rewarded, address reward, uint48 epoch1, uint48 epoch2, uint48 epoch3
)
    epoch1 != epoch2 &&  epoch1 != epoch3  && epoch3 != epoch2 => (
        rewardAmount(rewarded, reward, epoch1) +
        rewardAmount(rewarded, reward, epoch2) +
        rewardAmount(rewarded, reward, epoch3) <=
        to_mathint(totalRewardRegistered(rewarded, reward))
    );


/// @title The `SCALER` - since we cannot use constants
definition SCALER() returns uint256 = 2* 10^19;

/// @title `totalRewardRegistered` cannot be too large
invariant totalRegisteredIsNotBig(address rewarded, address reward)
    totalRewardRegistered(rewarded, reward) * SCALER() <= max_uint160;


/// @title The `MAX_EPOCH_DURATION` (70 days) - since we cannot use constants
definition MAX_EPOCH_DURATION() returns uint256 = 10 * 7 * 24 * 60 * 60;

/// @title `EPOCH_DURATION` is not larger than `MAX_EPOCH_DURATION`
invariant EpochDurationSizeLimit()
    currentContract.EPOCH_DURATION <= MAX_EPOCH_DURATION();


    
    

// ---- Eligible change equals staked change -----------------------------------

/// @title Ghost counting the number of times the distribution of `reward` accessed
persistent ghost mapping(address => mathint) timesAccessed;


/// @notice Hook onto the writing of `totalEligible`
hook Sstore distributions[KEY address rewarded][KEY address reward].totalEligible
    uint256 newAmount
{
    timesAccessed[reward] = timesAccessed[reward] + 1;
}


/// @title The change in `totalEligible` equals the change in staked balance
rule eligibleRelational(address rewarded, uint256 amount, address reward) {

    env e;
    require e.msg.sender != currentContract.evc;

    uint256 preBalance = balanceOf(e.msg.sender, rewarded);
    uint256 preTotal = currentContract.distributions[rewarded][reward].totalEligible;

    timesAccessed[reward] = 0;
    stake(e, rewarded, amount);

    // This is sound since elements in `Set.sol` are unique, and since `totalEligible`
    // is changed once per reward.
    require timesAccessed[reward] == 1;

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);
    uint256 postTotal = currentContract.distributions[rewarded][reward].totalEligible;

    assert (
        postTotal - preTotal == postBalance - preBalance,
        "change in total eligible equals change in staked"
    );
}
