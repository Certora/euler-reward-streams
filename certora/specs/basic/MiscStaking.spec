/* Miscellaneous rules for `StakingRewardStreams` */
using DummyERC20 as _ERC20;

methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    
    function DummyERC20.balanceOf(address) external returns (uint256) envfree;

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
