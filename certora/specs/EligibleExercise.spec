/* Rules for `StakingRewardStreams` */
methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    
    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
}

/// @title Ghost counting the number of times the distribution of `reward` changed
persistent ghost mapping(address => mathint) timesAccessed;


/// @notice Hook onto the writing of `totalEligible` and update `timesAccessed`
hook Sstore // TODO: complete the hook 
{
    // TODO: complete the hook's body
}


/// @title The change in `totalEligible` equals the change in staked balance when calling
/// `stake`
rule eligibleRelationalFirst(address rewarded, uint256 amount, address reward) {
    // TODO: complete the rule
}
