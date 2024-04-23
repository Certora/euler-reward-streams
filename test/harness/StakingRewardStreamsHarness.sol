// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.24;

import "../../src/StakingRewardStreams.sol";

contract StakingRewardStreamsHarness is StakingRewardStreams {
    using SafeERC20 for IERC20;
    using Set for SetStorage;

    constructor(address evc, uint48 epochDuration) StakingRewardStreams(evc, epochDuration) {}

    function setDistributionAmount(address rewarded, address reward, uint48 epoch, uint128 amount) external {
        distributionAmounts[rewarded][reward][epoch / EPOCHS_PER_SLOT][epoch % EPOCHS_PER_SLOT] = amount;
    }

    function getDistributionData(address rewarded, address reward) external view returns (DistributionStorage memory) {
        return distributionData[rewarded][reward];
    }

    function setDistributionData(
        address rewarded,
        address reward,
        DistributionStorage calldata distributionStorage
    ) external {
        distributionData[rewarded][reward] = distributionStorage;
    }

    function getDistributionTotals(address rewarded, address reward) external view returns (TotalsStorage memory) {
        return distributionTotals[rewarded][reward];
    }

    function setDistributionTotals(address rewarded, address reward, TotalsStorage calldata totalsStorage) external {
        distributionTotals[rewarded][reward] = totalsStorage;
    }

    function getAccountBalance(address account, address rewarded) external view returns (uint256) {
        return accounts[account][rewarded].balance;
    }

    function setAccountBalance(address account, address rewarded, uint256 balance) external {
        accounts[account][rewarded].balance = balance;
    }

    function insertReward(address account, address rewarded, address reward) external {
        accounts[account][rewarded].enabledRewards.insert(reward);
    }

    function getAccountEarnedData(
        address account,
        address rewarded,
        address reward
    ) external view returns (EarnStorage memory) {
        return accounts[account][rewarded].earned[reward];
    }

    function setAccountEarnedData(
        address account,
        address rewarded,
        address reward,
        EarnStorage memory earnStorage
    ) external {
        accounts[account][rewarded].earned[reward] = earnStorage;
    }
}
