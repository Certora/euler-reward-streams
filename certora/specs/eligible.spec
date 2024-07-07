/* Rules for `StakingRewardStreams` */
methods {
    function balanceOf(address, address) external returns (uint256) envfree;
    
    // `ERC20` dispatching
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
}

// ---- First solution for relational rule for `totalEligible` -----------------

/// @title Ghost counting the number of times the distribution of `reward` accessed
persistent ghost mapping(address => mathint) timesAccessed;


/// @notice Hook onto the writing of `totalEligible`
hook Sstore distributions[KEY address rewarded][KEY address reward].totalEligible uint256 newAmount {
    timesAccessed[reward] = timesAccessed[reward] + 1;
}


/// @title The change in `totalEligible` equals the change in staked balance
/// @notice This solution is PROBLEMATIC, since it relies on `totalEligible` being
/// changed only once per reward.
rule eligibleRelationalFirst(address rewarded, uint256 amount, address reward) {

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

// ---- Second solution for relational rule for `totalEligible` ----------------

definition elements(address msgSender, address rewarded, uint8 i) returns address = (
    currentContract.accounts[msgSender][rewarded].enabledRewards.elements[i].value
);

definition firstElement(address msgSender, address rewarded) returns address = (
    currentContract.accounts[msgSender][rewarded].enabledRewards.firstElement
);


/// @title Requires that elements of `enabledRewards` are unique
function setElementsUniqueness(address msgSender, address rewarded) {
    uint8 numElements = currentContract.accounts[msgSender][rewarded].enabledRewards.numElements;

    require (
        forall uint8 i. forall uint8 j.
        (0 < i && i < j && j < numElements) => (
            elements(msgSender, rewarded, i) !=  elements(msgSender, rewarded, i)
        )
    );

    require (
        forall uint8 i. (0 < i && i < numElements) => (
            elements(msgSender, rewarded, i) !=  firstElement(msgSender, rewarded)
        )
    );
}


/// @title Requires that reward is one of the enabled rewards
function contains(address msgSender, address rewarded, address reward) {
    uint8 numElements = currentContract.accounts[msgSender][rewarded].enabledRewards.numElements;
    require (
        reward == firstElement(msgSender, rewarded) && numElements > 0 ||
        !(forall uint8 i. (
            0 == i || i >= numElements || elements(msgSender, rewarded, i) != reward
        ))
    );
}


/// @title The change in `totalEligible` equals the change in staked balance
rule eligibleRelationalSecond(address rewarded, uint256 amount, address reward) {

    env e;
    require e.msg.sender != currentContract.evc;
    setElementsUniqueness(e.msg.sender, rewarded);
    contains(e.msg.sender, rewarded, reward);

    uint256 preBalance = balanceOf(e.msg.sender, rewarded);
    uint256 preTotal = currentContract.distributions[rewarded][reward].totalEligible;

    stake(e, rewarded, amount);

    uint256 postBalance = balanceOf(e.msg.sender, rewarded);
    uint256 postTotal = currentContract.distributions[rewarded][reward].totalEligible;

    assert (
        postTotal - preTotal == postBalance - preBalance,
        "change in total eligible equals change in staked"
    );
}
