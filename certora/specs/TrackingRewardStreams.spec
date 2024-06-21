methods {
    function getRewards(address rewarded, address account) external returns (address[] memory) envfree;
    function getDistribution_lastUpdated(address rewarded, address reward) external returns (uint48) envfree;
    function getDistribution_accumulator(address rewarded, address reward) external returns (uint208) envfree;
    function getDistribution_totalEligible(address rewarded, address reward) external returns (uint256) envfree;
    function getDistribution_totalRegistered(address rewarded, address reward) external returns (uint128) envfree;
    function getDistribution_totalClaimed(address rewarded, address reward) external returns (uint128) envfree;
    function getEarnedStorage_accumulator(address rewarded, address account, address reward) external returns (uint160) envfree;
    function getEarnedStorage_claimable(address rewarded, address account, address reward) external returns (uint96) envfree;
    function getCurrentAccountBalance(address rewarded, address account) external returns (uint256) envfree;
}

function perRewardAssumptions(address rewarded, address account, 
    uint256 newAccountBalance, address reward) returns bool {
    // https://prover.certora.com/output/65266/64f9a1d666d44427b295263d9c7c47fa/?anonymousKey=60293ef045d8c104272bea58129bd8f656798ee0
    // prevent overflow calculateRewards in BaseRewardStreams.sol line 628
    // Need to make this assumption from comments: 
    // Downcasting is safe because the `totalRegistered <= type(uint160).max / SCALER < type(uint96).max`.
    bool totalRegisteredBound = getDistribution_totalRegistered(rewarded, reward) < max_uint96;

    // https://prover.certora.com/output/65266/66a34c860dd343dab0d0737f3a88be17?anonymousKey=dce17147401b71e97c4c52869c3046af25945bc9
    // uint256(accumulator - accountEarnStorage.accumulator) // prevent this overflow
    uint208 accumulator = getDistribution_accumulator(rewarded, reward);
    uint160 accountEarnStorageAcc = getEarnedStorage_accumulator(rewarded, account, reward);
    bool accumulatorBound = accumulator > assert_uint208(accountEarnStorageAcc);

    // https://prover.certora.com/output/65266/1915458f51704743bb9119d036b499fc?anonymousKey=fa241fa735ffdd3a8d7317464802162378d90c8b
    // TrackingRwardStreams.sol Line 56 overflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance) - 
    //       currentAccountBalance;
    uint256 oldTotalEligible = getDistribution_totalEligible(rewarded, reward);
    bool totalEligibleBound = oldTotalEligible + newAccountBalance < max_uint256;

    // https://prover.certora.com/output/65266/b23921a609cd4936986e07d859d24bb3?anonymousKey=022642c5754cfa07b1fff3a9ce660ff958f356e6
    // TrackingRwardStreams.sol Line 56 overflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance - 
    //       currentAccountBalance);
    uint256 currentAccountBalance = getCurrentAccountBalance(rewarded, account);
    bool newTotalEligibleUpperBound = (oldTotalEligible +
        newAccountBalance - currentAccountBalance) < max_uint256;

    // https://prover.certora.com/output/65266/1915458f51704743bb9119d036b499fc/?anonymousKey=fa241fa735ffdd3a8d7317464802162378d90c8b
    // TrackingRwardStreams.sol Line 56 underflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance - 
    //       currentAccountBalance);
    // The require_uint256 is justified by totalEligibleBound
    bool newTotalEligibleLowerBound = require_uint256(oldTotalEligible +
            newAccountBalance) > currentAccountBalance;

    // https://prover.certora.com/output/65266/6588bf95123c4aa0b36fec7179feec27/?anonymousKey=685792f8e3ecae621945b3c6c11b78c4d10c4b40
    // BaseRewardStreams.sol Line 629, overflow part in these brackets: [[ ]]
    // Note: this is a distinct assumption from the comment in the code:
    // Downcasting is safe because the `totalRegistered <= type(uint160).max / SCALER < type(uint96).max`.
    //         claimable += uint96(uint256( [[accumulator - accountEarnStorage.accumulator) * currentAccountBalance]] / SCALER);
    mathint claimableSubExpr= (accumulator - accountEarnStorageAcc) * currentAccountBalance;
    bool claimableSubExprBoundUpper = claimableSubExpr < max_uint256;

    // https://prover.certora.com/output/65266/5719d5fc723c4edeb901476edf0fdcbe/?anonymousKey=88cffe1bf1dc68fd9c46a1fdfb72f0a4b6e698c8
    // TODO I suspect overflow of old claimable + new claimable
    //         claimable += uint96(uint256(accumulator - accountEarnStorage.accumulator) * currentAccountBalance / SCALER);
    // BaseRewardStreams.sol Line 629
    mathint oldClaimable = getEarnedStorage_claimable(rewarded, account, reward);
    mathint scaler = 20000000000000000000;
    bool claimableBoundUpper = oldClaimable + claimableSubExpr / scaler < max_uint96;

    return totalRegisteredBound && 
        accumulatorBound &&
        totalEligibleBound &&
        newTotalEligibleUpperBound &&
        newTotalEligibleLowerBound &&
        claimableSubExprBoundUpper &&
        claimableBoundUpper;

}

rule balanceTrackerHookDoesNotRevert {
    env e;
    address account;
    uint256 newAccountBalance;
    // assuming forfeitRecentReward == true


    address rewarded = e.msg.sender;
    address[] rewards = currentContract.getRewards(rewarded, account);

    // loop bound
    require rewards.length == 2;
    require perRewardAssumptions(rewarded, account, newAccountBalance, rewards[0]);
    require perRewardAssumptions(rewarded, account, newAccountBalance, rewards[1]);

    // https://prover.certora.com/output/65266/390e99a158214c2a83351c18c288e954/?anonymousKey=ec2aa4ec5ec8906cd6d72a4faa0bc656d08f9398
    require e.msg.value == 0;

    // This assumption is a bit contrived, but if we do not make it,
    // we run into this counterexample. In this counterexample rewards[0]
    // == rewards[1] and the assumption "newTotalEligibleUpperBound"
    // is not strong enough because in the first loop iteration
    // the totalEligible gets increased and this is violated in
    // the second loop iteration (which works on the same reward address
    // https://prover.certora.com/output/65266/6453dec1b3574736851ec6b75935ed51/?anonymousKey=6d6d52633c709383c62015ed035d9e3da727b847
    require rewards[0] != rewards[1];

    balanceTrackerHook@withrevert(e, account, newAccountBalance, true);
    assert !lastReverted;
}