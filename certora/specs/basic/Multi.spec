/* Multi setup for `StakingRewardStreams` */
using DummyERC20A as _ERC20;

methods {
    // Main contract
    function balanceOf(address, address) external returns (uint256) envfree;
    
    // Dummies
    function DummyERC20A.balanceOf(address) external returns (uint256) envfree;
    function DummyERC20B.balanceOf(address) external returns (uint256) envfree;
    function DummyERC20A.totalSupply() external returns (uint256) envfree;
//    function DummyERC20C.balanceOf(address) external returns (uint256) envfree;
//    function DummyERC20D.balanceOf(address) external returns (uint256) envfree;

    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);

    function externalBalanceOf(address, address) external returns (uint256) envfree;
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


/// @title Staking increases staked balance by given amount
rule stakeIntergrity(address rewarded, uint256 amount) {
    env e;
    setup(e);

    require e.msg.sender != currentContract.evc;
    uint256 xBefore = externalBalanceOf(rewarded,e.msg.sender );
    uint256 preBalance = balanceOf(e.msg.sender, rewarded);

    stake(e, rewarded, amount);

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);
    uint256 xAfter = externalBalanceOf(rewarded,e.msg.sender );

    assert (
        (amount != max_uint256 => to_mathint(postBalance) == preBalance + amount)
        && (amount == max_uint256 => postBalance >= preBalance ),
        "Staking increases staked balance by given amount"
    );
    assert (xBefore + preBalance == xAfter + postBalance );
    
}

function setup(env e) {
    require e.msg.sender != currentContract; 
    require e.msg.sender != currentContract.evc;
}

rule stakeUnstake(address rewarded, uint256 amount , address user) {

    env e; 
    bool b;
    address r;
    setup(e);

    uint256 preBalance = balanceOf(user, rewarded);
    unstake(e, rewarded, amount,r, b);

    uint256 postBalance = balanceOf(user, rewarded);
    assert postBalance != preBalance <=> e.msg.sender == user; 
}


 ghost mathint sumOfBalances_ERC20A {
    // `init_state` determines the state after the constructor
    init_state axiom sumOfBalances_ERC20A == 0;
}


// Update the sum of balances
hook Sstore _ERC20._balances[KEY address addr] uint256 newValue (uint256 oldValue) {
    // Update the sum whenever a balance changes
    sumOfBalances_ERC20A = sumOfBalances_ERC20A - oldValue + newValue;
}


/// @title `totalSupply` is the sum of all balances
invariant totalSupplyIsSumOfBalances_ERC20A()
    to_mathint(_ERC20.totalSupply()) == sumOfBalances_ERC20A; 

rule simpleSimpleSolvency(method f, address token) {

    uint256 preBalance = externalBalanceOf(token, currentContract);
    requireInvariant totalSupplyIsSumOfBalances_ERC20A();

    env e;
    calldataarg args;
    f(e,args);

    uint256 postBalance = externalBalanceOf(token, currentContract);

    assert postBalance < preBalance => 
        // on certrain functions
        f.selector == sig:unstake(address,uint256,address,bool).selector ||
        f.selector == sig:claimReward(address,address,address,bool).selector ||
        f.selector == sig:updateReward(address,address,address).selector  ; 
}

