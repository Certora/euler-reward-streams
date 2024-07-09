/* Invariants and parametric rules for `StakingRewardStreams` */
methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    function rewardAmount(address, address, uint48) external returns (uint256) envfree;
    function totalRewardClaimed(address, address) external returns (uint256) envfree;
    function totalRewardRegistered(address, address) external returns (uint256) envfree;
}


/// @title Total claimed is non-decreasing (parametric rule)
rule totalClaimedIsNonDecreasing(method f, address rewarded, address reward) {
    // TODO
}


/// @title Staked balance is reduced only by calling `unstake`
rule stakedReduceProperty(method f, address account, address rewarded) {
    // TODO
}


/// @title Reward amount per epoch is not greater than total registered reward
invariant rewardAmountLessThanTotal(address rewarded, address reward, uint48 epoch)
    // TODO


/// @title The sum of rewards of two different epochs is not greater than total
/// registered reward
invariant rewardSumLessThanTotal(
    address rewarded, address reward, uint48 epoch1, uint48 epoch2
)
    // TODO
