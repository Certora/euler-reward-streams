/* Rules for `StakingRewardStreams` */
using DummyERC20 as _ERC20;

methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    
    function DummyERC20.balanceOf(address) external returns (uint256) envfree;

    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
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

// ---- Eligible change equals staked change -----------------------------------

/// @title Ghost counting the number of times the distribution of `reward` accessed
persistent ghost mapping(address => mathint) timesAccessed;


/// @notice Hook onto the writing of `totalEligible`
hook Sstore distributions[KEY address rewarded][KEY address reward].totalEligible uint256 newAmount {
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
