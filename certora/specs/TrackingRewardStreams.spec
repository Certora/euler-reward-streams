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

function perRewardAssumptions(address rewarded, address account, uint256 newAccountBalance, address reward) returns bool {
    mathint scaler = 20000000000000000000;
    uint128 totalRegistered = getDistribution_totalRegistered(rewarded, reward);
    uint208 accumulator = getDistribution_accumulator(rewarded, reward);

    // refined assumption as per https://github.com/euler-xyz/reward-streams/blob/master/src/BaseRewardStreams.sol#L183-L185
    bool totalRegisteredBound = totalRegistered <= assert_uint128(max_uint160 / scaler);

    // additional assumption for the accumulator, same reasoning as above
    bool accumulatorBound = accumulator <= assert_uint208(totalRegistered * scaler);

    // accumulator can only grow
    uint160 accountEarnStorageAcc = getEarnedStorage_accumulator(rewarded, account, reward);
    bool userAccumulatorBound = accumulator >= assert_uint208(accountEarnStorageAcc);

    // this should be enough not to revert. neither old nor new claimable by a single user can be greater than total registered rewards. this should contain user balance because in practice it cannot be greater than the total eligible balance of all the users
    uint256 currentAccountBalance = getCurrentAccountBalance(rewarded, account);
    mathint oldClaimable = getEarnedStorage_claimable(rewarded, account, reward);
    mathint newClaimable = oldClaimable + (accumulator - accountEarnStorageAcc) * currentAccountBalance / scaler;
    bool claimableBoundUpper = require_uint128(oldClaimable) <= totalRegistered && require_uint128(newClaimable) <= totalRegistered;
    // assert_uint128 for newClaimable fails, so we need require_uint128:
    // https://prover.certora.com/output/65266/1ac07e47fa6343a2bef2b8325457e079?anonymousKey=56fc5fd764c88bdc56ec428259b21ccc0a89d3cc
    // This does not introduce an extra assumption though because we already
    // assume it is less than totalRegistered wich is a uint128

    // https://prover.certora.com/output/65266/1915458f51704743bb9119d036b499fc?anonymousKey=fa241fa735ffdd3a8d7317464802162378d90c8b
    // TrackingRwardStreams.sol Line 56 overflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance) - 
    //       currentAccountBalance;
    uint256 oldTotalEligible = getDistribution_totalEligible(rewarded, reward);
    bool totalEligibleBound = oldTotalEligible + newAccountBalance <= max_uint256;

    // https://prover.certora.com/output/65266/b23921a609cd4936986e07d859d24bb3?anonymousKey=022642c5754cfa07b1fff3a9ce660ff958f356e6
    // TrackingRwardStreams.sol Line 56 overflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance - 
    //       currentAccountBalance);
    bool newTotalEligibleUpperBound = (oldTotalEligible +
        newAccountBalance - currentAccountBalance) <= max_uint256;

    // https://prover.certora.com/output/65266/1915458f51704743bb9119d036b499fc/?anonymousKey=fa241fa735ffdd3a8d7317464802162378d90c8b
    // TrackingRwardStreams.sol Line 56 underflow in parenthesis here
    // distributionStorage.totalEligible =
    // (distributionStorage.totalEligible + newAccountBalance - 
    //       currentAccountBalance);
    // The require_uint256 is justified by totalEligibleBound
    bool newTotalEligibleLowerBound = require_uint256(oldTotalEligible +
            newAccountBalance) >= currentAccountBalance;

    return totalRegisteredBound && 
        accumulatorBound &&
        userAccumulatorBound &&
        claimableBoundUpper &&
        totalEligibleBound &&
        newTotalEligibleUpperBound &&
        newTotalEligibleLowerBound;
}

// Passing.
// Run link: https://prover.certora.com/output/65266/3a141e6327124fe3b46053cec3b43c0b?anonymousKey=fb807844ed13f892a78c2226a083162cbf3828c7
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