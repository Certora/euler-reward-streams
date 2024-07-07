/* Multi setup for `StakingRewardStreams` */
using DummyERC20A as _ERC20;

methods {
    // Main contract
    function balanceOf(address, address) external returns (uint256) envfree;
    
    // Dummies
    function DummyERC20A.balanceOf(address) external returns (uint256) envfree;
    function DummyERC20B.balanceOf(address) external returns (uint256) envfree;
    function DummyERC20C.balanceOf(address) external returns (uint256) envfree;
    function DummyERC20D.balanceOf(address) external returns (uint256) envfree;

    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
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
