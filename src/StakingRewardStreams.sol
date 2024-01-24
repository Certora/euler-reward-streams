// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.23;

import "./BaseRewardStreams.sol";

/// @title StakingRewardStreams
/// @notice This contract inherits from BaseRewardStreams and implements IStakingRewardStreams interface.
/// It allows for the rewards to be distributed to the rewarded token holders who have staked it.
contract StakingRewardStreams is BaseRewardStreams, IStakingRewardStreams {
    using SafeERC20 for IERC20;
    using Set for SetStorage;

    /// @notice Event emitted when a user stakes tokens.
    event Staked(address indexed account, address indexed rewarded, uint256 amount);

    /// @notice Event emitted when a user unstakes tokens.
    event Unstaked(address indexed account, address indexed rewarded, uint256 amount);

    /// @notice Constructor for the StakingRewardStreams contract.
    /// @param evc The Ethereum Vault Connector contract.
    /// @param periodDuration The duration of a period.
    constructor(IEVC evc, uint40 periodDuration) BaseRewardStreams(evc, periodDuration) {}

    /// @notice Allows a user to stake rewarded tokens.
    /// @dev If the amount is max, the entire balance of the user is staked.
    /// @param rewarded The address of the rewarded token.
    /// @param amount The amount of tokens to stake.
    function stake(address rewarded, uint256 amount) external virtual override nonReentrant {
        address msgSender = _msgSender();

        if (amount == 0) {
            revert InvalidAmount();
        } else if (amount == type(uint256).max) {
            amount = IERC20(rewarded).balanceOf(msgSender);
        }

        uint256 currentBalance = balances[msgSender][rewarded];
        address[] memory rewardsArray = rewards[msgSender][rewarded].get();

        for (uint256 i; i < rewardsArray.length; ++i) {
            address reward = rewardsArray[i];
            uint256 currentTotal = distribution[rewarded][reward].totalEligible;

            updateRewardTokenData(msgSender, rewarded, reward, currentTotal, currentBalance, false);

            distribution[rewarded][reward].totalEligible = currentTotal + amount;
        }

        balances[msgSender][rewarded] = currentBalance + amount;

        uint256 oldBalance = IERC20(rewarded).balanceOf(address(this));
        IERC20(rewarded).safeTransferFrom(msgSender, address(this), amount);

        // If the balance of the contract did not increase by the staked amount, revert.
        if (IERC20(rewarded).balanceOf(address(this)) - oldBalance != amount) {
            revert InvalidAmount();
        }

        emit Staked(msgSender, rewarded, amount);
    }

    /// @notice Allows a user to unstake rewarded tokens.
    /// @dev If the amount is max, the entire balance of the user is unstaked.
    /// @param rewarded The address of the rewarded token.
    /// @param recipient The address to receive the unstaked tokens.
    /// @param amount The amount of tokens to unstake.
    /// @param forgiveRecentReward Whether to forgive the recent reward and not update the accumulator.
    function unstake(
        address rewarded,
        uint256 amount,
        address recipient,
        bool forgiveRecentReward
    ) external virtual override nonReentrant {
        address msgSender = _msgSender();

        if (amount == 0) {
            revert InvalidAmount();
        } else if (amount == type(uint256).max) {
            amount = balances[msgSender][rewarded];
        }

        uint256 currentBalance = balances[msgSender][rewarded];
        address[] memory rewardsArray = rewards[msgSender][rewarded].get();

        for (uint256 i; i < rewardsArray.length; ++i) {
            address reward = rewardsArray[i];
            uint256 currentTotal = distribution[rewarded][reward].totalEligible;

            updateRewardTokenData(msgSender, rewarded, reward, currentTotal, currentBalance, forgiveRecentReward);

            distribution[rewarded][reward].totalEligible = currentTotal - amount;
        }

        balances[msgSender][rewarded] = currentBalance - amount;

        IERC20(rewarded).safeTransfer(recipient, amount);

        emit Unstaked(msgSender, rewarded, amount);
    }
}
