# EVM Wallet Safety Kit

A small, read-only toolkit to check what an EVM wallet has approved, and to
clean up after using a mint / claim / airdrop site.

No private keys. No seed phrases. No signing. The scripts only read public
on-chain data through a public RPC endpoint.

## Why this exists

After a free mint or claim, the risky part is often not the mint itself — it
is what is left behind:

- an unlimited ERC-20 allowance (`approve(spender, 2**256 - 1)`) to a
  contract you may never use again,
- a dApp session still connected in your wallet,
- a token approval you forgot you granted months ago.

This kit gives you a repeatable check for that, in under a minute.

## What is inside

| File | What it does |
| --- | --- |
| `src/check_allowances.py` | Lists ERC-20 `allowance(owner, spender)` for the tokens and spenders you list, flags unlimited approvals, and prints a plain-text report. Read-only, standard library only. |
| `src/revoke_calldata.py` | Builds the `approve(spender, 0)` calldata to revoke an allowance, without sending anything. You review it, then send it yourself in your wallet. |
| `CHECKLIST.md` | The post-mint / post-claim checklist: disconnect, check, revoke, verify. |
| `docs/REVOKE-GUIDE.md` | How to revoke safely, and when *not* to revoke yet. |
| `docs/CHAINS.md` | Chain IDs and public RPCs used by the scripts. |
| `examples/config.example.json` | Example config — copy it, fill in your own wallet and contracts. |

## Quick start

```bash
# 1. Copy the example config
cp examples/config.example.json my-config.json

# 2. Edit my-config.json with your wallet address,
#    the tokens you hold, and the spenders to check.
#    Never put a private key or seed phrase in this file.

# 3. Check allowances on BNB Smart Chain (56)
python3 src/check_allowances.py --config my-config.json --chain bsc

# 4. Check another chain
python3 src/check_allowances.py --config my-config.json --chain ethereum
```

Sample output:

```text
Chain: BSC (56)  Wallet: 0x1234...abcd
Token USDT (18 decimals)  balance: 12.5
  spender 0x10ED...24E (PancakeSwap Router)  allowance: UNLIMITED (2**256-1)  <-- review
  spender 0x3E9B...A00f (Example Mint)       allowance: 0
```

## Safety rules

1. **Read-only first.** Run `check_allowances.py` before you revoke
   anything. It never sends a transaction.
2. **Never share a seed phrase or private key** — not with this repo, not
   with any site, not with anyone offering to "help" revoke for you.
3. **Revoke unlimited approvals you no longer need**, especially to mint /
   claim contracts from one-off projects.
4. **Do not revoke an approval you still need** for an open position, a
   staking contract, or a bridge in flight. See `docs/REVOKE-GUIDE.md`.
5. **Disconnect the dApp session** after you finish, unless you deliberately
   keep that one site connected. Keep a short allowlist — see `CHECKLIST.md`.
6. **Verify after revoking.** Re-run the checker and confirm the allowance
   is now `0`.

## Supported chains

BNB Smart Chain (56), Ethereum (1), Robinhood Chain (4663), Sepolia (11155159).
Add your own in `src/check_allowances.py` (`CHAINS`) or in your config file
(`"rpc_url"` overrides the default).

## Requirements

- Python 3.10+
- No third-party packages. The scripts use only the standard library
  (`urllib`, `json`, `argparse`).

## License

MIT — see `LICENSE`.
