/* Basic rules for `StakingRewardStreams` */
methods {
    function balanceOf(address, address) external returns (uint256) envfree;
}


/// @title Staking increases staked balance by given amount - wrong
/// @notice This rule is violated!
rule stakeIntergritySimpleWrong(address rewarded, uint256 amount) {
    env e;
    uint256 preBalance = balanceOf(e.msg.sender, rewarded);

    stake(e, rewarded, amount);

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);

    assert (
        to_mathint(postBalance) == preBalance + amount,
        "Staking increases staked balance by given amount"
    );
}


/// @title Staking increases staked balance by given amount - wrong
/// @notice This rule is violated!
rule stakeIntergrityWrong(address rewarded, uint256 amount) {
    env e;

    // Direct storage access
    // Why is this requirement needed?
    require e.msg.sender != currentContract.evc;
    
    uint256 preBalance = balanceOf(e.msg.sender, rewarded);

    stake(e, rewarded, amount);

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);

    assert (
        to_mathint(postBalance) == preBalance + amount,
        "Staking increases staked balance by given amount"
    );
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
