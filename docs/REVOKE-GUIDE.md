# Revoke Guide

## What an allowance is

When you `approve(spender, amount)` an ERC-20 token, you let that spender
move up to `amount` of that token out of your wallet without asking again.
An unlimited approval is `amount = 2**256 - 1`. It is convenient for a
contract you use often, and risky for a contract you used once.

## How to revoke

1. Check first — `src/check_allowances.py` shows what is approved.
2. Revoke by sending `approve(spender, 0)` to the **token** contract,
   with value `0`. You can build that calldata with
   `src/revoke_calldata.py`, or use a revoke tool you trust
   (for example Revoke.cash, or the token-approval checker on the chain's
   block explorer).
3. Verify — re-run the checker. The allowance should read `0`.

Revoking costs gas, but it is a normal transaction on the same chain as
the approval.

## When to revoke

Revoke when:

- the approval is unlimited and the spender is a one-off mint / claim
  contract you will not use again;
- the project is over, paused, or you do not recognise the spender;
- you are cleaning up after an airdrop season.

## When NOT to revoke yet

Do not revoke when:

- you still have funds staked, deposited, or bridged through that spender;
- the spender is a router / vault you actively use;
- a transaction is still in flight that depends on that approval.

Revoking early does not lose your tokens, but it can block a withdrawal or
unstake until you approve again — so check the position first.

## A note on sessions vs. approvals

Disconnecting a dApp session and revoking an allowance are two different
things. Disconnecting stops the site talking to your wallet. Revoking stops
the contract moving your tokens. After a mint or claim, do both.
