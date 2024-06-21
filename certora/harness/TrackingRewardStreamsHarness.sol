// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.0;
import "../../src/TrackingRewardStreams.sol";

contract TrackingRewardStreamsHarness is TrackingRewardStreams {
    using Set for SetStorage;
    constructor(address evc, uint48 epochDuration) TrackingRewardStreams(evc, epochDuration) {}

    function getRewards(address rewarded, address account) external returns (address[] memory rewards) {
        AccountStorage storage accountStorage = accounts[account][rewarded];
        return accountStorage.enabledRewards.get();
    }

    function getCurrentAccountBalance(address rewarded, address account) external returns (uint256) {
        AccountStorage storage accountStorage = accounts[account][rewarded];
        return accountStorage.balance;
    }


    function getDistribution_lastUpdated(address rewarded, address reward) external returns (uint48) {
        return distributions[rewarded][reward].lastUpdated;
    }
    function getDistribution_accumulator(address rewarded, address reward) external returns (uint208) {
        return distributions[rewarded][reward].accumulator;
    }
    function getDistribution_totalEligible(address rewarded, address reward) external returns (uint256) {
        return distributions[rewarded][reward].totalEligible;
    }
    function getDistribution_totalRegistered(address rewarded, address reward) external returns (uint128) {
        return distributions[rewarded][reward].totalRegistered;
    }
    function getDistribution_totalClaimed(address rewarded, address reward) external returns (uint128) {
        return distributions[rewarded][reward].totalClaimed;
    }

    function getEarnedStorage_accumulator(address rewarded, address account, address reward) external returns (uint160) {
        AccountStorage storage accountStorage = accounts[account][rewarded];
        return accountStorage.earned[reward].accumulator;
    }

    function getEarnedStorage_claimable(address rewarded, address account, address reward) external returns (uint96) {
        AccountStorage storage accountStorage = accounts[account][rewarded];
        return accountStorage.earned[reward].claimable;
    }
}