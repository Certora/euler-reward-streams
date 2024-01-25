# Reward Streams - Efficient and Flexible Reward Distribution

Reward Streams is a powerful and flexible implementation of the billion-dollar algorithm, a popular method for proportional reward distribution in the Ethereum developer community. This project extends the algorithm's functionality to support both staking and staking-free reward distribution, multiple reward tokens, and permissionless registration of reward distribution schemes. This makes Reward Streams a versatile tool for incentivizing token staking and holding in a variety of use cases.

---

## Contracts

```
.
├── interfaces
│   ├── IBalanceForwarder.sol
│   ├── IBalanceTracker.sol
│   └── IRewardStreams.sol
├── BaseRewardStreams.sol
├── StakingFreeRewardStreams.sol
└── StakingRewardStreams.sol
```

## The billion-dollar algorithm

The billion-dollar algorithm is a method for efficient incremental calculation of proportional reward distribution. It works by dividing the total reward pool proportionally among participants based on their stake. It does this incrementally, updating the distribution as new stakes are added or existing ones are removed. This allows the algorithm to handle large numbers of participants and high transaction volumes efficiently.

This algorithm was first described in [Scalable Reward Distribution on the Ethereum Blockchain](https://uploads-ssl.webflow.com/5ad71ffeb79acc67c8bcdaba/5ad8d1193a40977462982470_scalable-reward-distribution-paper.pdf) by Bogdan Batog, Lucian Boca, and Nick Johnson. It gained popularity in 2019, with the first [liquidity mining program](https://sips.synthetix.io/sips/sip-31/) being launched by Synthetix for the sETH Uniswap pool. The initial [smart contract](https://github.com/k06a/Unipool/commit/e4bdb0a978fd498a1480e3d1bc4b4c1682c74c12#diff-0d1e350796b5338e3c326be95f9a9ad147d4695746306a50a9fdccf8dbbfd708) developed by Anton Bukov has been forked and adapted repeatedly over the years.

Today, the algorithm is used by many projects in the Ethereum ecosystem. For example, Uniswap v3 uses it to track fees earned by individual positions, SushiSwap uses it in its [MasterChef](https://medium.com/coinmonks/analysis-of-the-billion-dollar-algorithm-sushiswaps-masterchef-smart-contract-81bb4e479eb6) smart contract to incentivize liquidity providers, and 1inch has adapted it as part of their [ERC20Plugins concept](https://github.com/1inch/token-plugins) to allow [farming](https://github.com/1inch/farming?tab=readme-ov-file) without a need to stake tokens.

## Motivation

The billion-dollar algorithm has been a game-changer for reward distribution in the Ethereum ecosystem. However, existing implementations have limitations that can hinder their flexibility and utility. For instance, most implementations do not support staking-free reward distribution and join multiple farms that provide rewards for the same token.

Reward Streams was developed to address these limitations and provide a more flexible and powerful implementation of the billion-dollar algorithm. Here's what Reward Streams offers:

1. A common base contract (`BaseRewardStreams`) that is reused by both staking and staking-free mechanisms of rewards distribution.
2. An easy-to-use mechanism for staking-free reward distribution, which requires only a subtle change to the ERC-20 token contract.
3. A permissionless mechanism to create a reward distribution scheme, enabling anyone to incentivize staking/holding of any token with any reward.
4. The ability for users to earn up to 5 different reward tokens simultaneously for staking/holding of a single rewarded token.
5. Additive, fixed length epoch-based distribution of rewards where the reward rate may differ from epoch to epoch.
6. A mechanism allowing to create a reward distribution scheme for up to 25 epochs in one go.
7. Protection against reward tokens being lost in case nobody earns them.

## How does it work?

Reward Streams operates in two modes of rewards distribution: staking and staking-free. Each mode has a separate contract implementation.

### Staking-Free Reward Distribution

The staking-free `StakingFreeRewardStreams` implementation inherits from the `BaseRewardStreams` contract. It defines the `IBalanceTracker.balanceTrackerHook` function, which is required to be called on every transfer of the rewarded token if a user opted in for the hook to be called. 

In this mode, the rewarded token contract not only calls the `balanceTrackerHook` function whenever a given account balance changes, but also implements the `IBalanceForwarder` interface. This interface defines two functions: `enableBalanceForwarding` and `disableBalanceForwarding`, which are used to opt in and out of the hook being called.

### Staking Reward Distribution

The staking `StakingRewardStreams` implementation also inherits from the `BaseRewardStreams` contract. It defines two functions: `stake` and `unstake`, which are used to stake and unstake the rewarded token.

In both modes, each distributor contract defines an `EPOCH_DURATION` constant, which is the duration of a single epoch. This duration cannot be less than 7 days. 

When registering a new `reward` distribution scheme for the `rewarded` token, one needs to specify the `startEpoch` number when the new distribution scheme will come into effect. `startEpoch` cannot be more than 5 epochs into the future. Moreover, one needs to specify `rewardAmounts` array which instructs the contract how much `reward` one wants to distribute in each epoch starting from `startEpoch`. The `rewardAmounts` array must have a length of at most 25.

If rewarded epochs of multiple distribution schemes overlap, the amounts will be combined and the effective distribution will be the sum of the amounts in the overlapping epochs.

---

### Example:

Let's consider a scenario where Alice and Bob want to incentivize `ABC` token staking with `DEF` reward. 

Alice wants to distribute `DEF` reward for 3 epochs starting from the next epoch. She specifies the `rewardAmounts` array as follows:
`rewardAmounts = [1e18, 1e18, 1e18]`. This means Alice wants to distribute 1 `DEF` token per epoch for the next 3 epochs.

Bob, on the other hand, wants to incentivize staking of the same `ABC` token with the same `DEF` reward. He wants to distribute `DEF` reward for 5 epochs starting one epoch later than Alice's distribution scheme. He specifies the `rewardAmounts` array as follows:
`rewardAmounts = [2e18, 2e18, 2e18, 2e18, 2e18]`. This means Bob wants to distribute 2 `DEF` tokens per epoch for the next 5 epochs, starting one epoch after Alice.

Considering that the amounts for the overlapping epochs get added, the effective distribution scheme will start from the next epoch and will look as follows:
`rewardAmounts = [1e18, 3e18, 3e18, 2e18, 2e18, 2e18]`

This means that in the first epoch, 1 `DEF` token will be distributed. In the second and third epoch, 3 `DEF` tokens will be distributed each. In the fourth, fifth, and sixth epoch, 2 `DEF` tokens will be distributed each.

---

For each account and rewarded token, each distributor contract maintains a set of enabled rewards. This feature is designed to prevent users from wasting gas on earning rewards they are not interested in. 

Suppose a user is interested in earning the `reward` token from the distribution which was permissionlessly set up for stakers/holders of the `rewarded` token. The user needs to explicitly express their preference by calling `enableReward` function with the `reward` token address and the `rewarded` token address. 

The user can also call `disableReward` function to stop earning the `reward` token for the `rewarded` token. This might be useful in situations where the user determines that the potential rewards do not justify the gas costs of participating in the distribution. 

A user may select up to 5 reward tokens to earn for a single rewarded token. This allows users to diversify their potential rewards and increase their potential earnings.

---

### Example:

Consider a scenario where the holding of token `ABC` is currently being incentivized with two types of rewards: `DEF` and `GHI`. Alice, a holder of `ABC` tokens, is evaluating which rewards to enable.

After examining the distributor parameters, Alice determines that accruing `DEF` reward does not make sense for her due to her small balance of `ABC` tokens versus the total balance currently earning `DEF`. She estimates that enabling `DEF` would not even compensate for the increased gas costs on `ABC` transfers.

Given this, Alice decides to enable only the `GHI` reward and keep the `DEF` reward disabled. This decision allows Alice to optimize her potential earnings while minimizing her costs.

---

Multiple functions of the distributors contain an additional boolean parameter called `forgiveRecentReward`. It allows a user to optimize gas consumption in case it is not worth to iterate over multiple distribution epochs and updating contract storage. It also allows for "emergency exit" for operations like disabling reward and claiming, and DOS protection (i.e. in liquidation flows).

As previously explained, rewards distributions are epoch-based. Thanks to that, each epoch may have a different reward rate, but also it is possible for the distribution schemes to be registered permissionlessly in additive manner. However, the downside of this approach is the fact that whenever a user stakes or unstakes (or, for staking-free version of the distributor, transfers/mints/burns the rewarded token), the distributor contract needs to iterate over all the epochs since the last time given distribution, defined by `rewarded` and `reward` token, was updated. Moreover, a user may be earning multiple rewards for a single rewarded token, so the distributor contract needs to iterate over all the epochs since the last update for all the rewards the user is earning. If updates happen rarely (i.e. due to low staking/unstaking activity), the gas cost associated with iterating may be significant, affecting user's profitability. Hence, when disabling or claiming reward, if the user wants to skip the epochs iteration, they can call the relevant function with `forgiveRecentReward` set to `true`. This will grant the rewards earned since the last distribution update, which would normally be earned by the user, to the rest of the distribution participants, lowering the gas cost for the user.

`forgiveRecentReward` parameter may also come handy for the rewarded token contract which calls `balanceTrackerHook` on the balance changes. In case of i.e. liquidation, where user may have incentive to perform DOS attack and increase gas cost of the token transfer by enabling multiple rewards for distributions of low activity, the rewarded token contract may call `balanceTrackerHook` with `forgiveRecentReward` set to `true` to lower the gas cost of the transfer. Unfortunately, this may lead to the user losing the rewards since the last update.

---

### Example:

Alice staked her `ABC` and decided to enable both `DEF` and `GHI` rewards. Alice now wants to unstake her `ABC`, but notices that despite her estimations `GHI` tokens that she earned have very low value. It's been some time since the `GHI` distribution was updated last time hence the gas cost associated with unstaking may be significant. Alice may decide to either call `unstake` with `forgiveRecentReward` set to `true`, which means that both `DEF` and `GHI` rewards that she would earn since the last updates would get lost in favor of the rest of participants. Or she may first call `disableReward(GHI)` with `forgiveRecentReward` set to `true`, which will skip epochs iteration for `GHI` distribution, and then call `unstake` with `forgiveRecentReward` set to `false`, keeping all the `DEF` rewards.

---

Unlike other permissioned distributors based on the billion-dollar algorithm, Reward Streams distributors do not have an owner or admin meaning that none of the assets can be directly recovered from them. This property is required in order for the system to work in a permissionless manner, allowing anyone to transfer rewards token to a distributor and register a new distribution scheme. The drawback of this approach is that reward tokens may get lost if nobody earns them at the given moment (i.e. nobody stakes required assets or nobody enabled earning those rewards). In order to prevent reward tokens from being lost when nobody earns them at the moment, the rewards get virtually accrued by address(0) and, in exchange for updating given distribution data, are claimable by anyone with use of `updateReward` function.

## Known limitations

1. **Epoch duration may not be shorter than 7 days**: This limitation is in place to ensure the stability and efficiency of the distribution system. The longer the epoch, the more gas efficient the distribution is.
2. **New distribution scheme may start at most 5 epochs ahead and be at most 25 epochs long**
3. **A user may have at most 5 rewards enabled at a time for a given rewarded token**: This limitation is in place to prevent users from enabling an excessive number of rewards, which could lead to increased gas costs and potential system instability.
4. **A distributor may distribute at most `type(uint160).max / 1e18` units of a reward token per rewarded token**
5. **A user may have at most `type(uint96).max` units of a reward token unclaimed per rewarded token**
6. **If nobody earns rewards at the moment (i.e. nobody staked yet), they're being virtually accrued by address(0) and may be claimed by anyone**: This feature is designed to prevent reward tokens from being lost when nobody earns them at the moment. However, it also means that unclaimed rewards could potentially be claimed by anyone.
7. **Distributor contracts do not have an owner or admin meaning that none of the assets can be directly recovered from them**: This feature is required for the system to work in a permissionless manner. However, it also means that if a mistake is made in the distribution of rewards, the assets cannot be directly recovered from the distributor contracts.


## Install

To install Ethereum Vault Connector in a [Foundry](https://github.com/foundry-rs/foundry) project:

```sh
forge install euler-xyz/reward-streams
```

## Usage

The Reward Streams repository comes with a comprehensive set of tests written in Solidity, which can be executed using Foundry.

To install Foundry:

```sh
curl -L https://foundry.paradigm.xyz | bash
```

This will download foundryup. To start Foundry, run:

```sh
foundryup
```

To clone the repo:

```sh
git clone https://github.com/euler-xyz/reward-streams.git && cd reward-streams
```

## Testing

### in `default` mode

To run the tests in a `default` mode:

```sh
forge test
```

### in `coverage` mode

```sh
forge coverage
```

## Safety

This software is **experimental** and is provided "as is" and "as available".

**No warranties are provided** and **no liability will be accepted for any loss** incurred through the use of this codebase.

Always include thorough tests when using the Reward Streams to ensure it interacts correctly with your code.

The Reward Streams are currently undergoing security audits and should not be used in production.

## Contributing

The code is currently in an experimental phase. Feedback or ideas for improving the Reward Streams are appreciated. Contributions are welcome from anyone interested in conducting security research, writing more tests including formal verification, improving readability and documentation, optimizing, simplifying, or developing integrations.

## License

Licensed under the [GPL-2.0-or-later](https://github.com/euler-xyz/reward-streams/tree/master/LICENSE) license.