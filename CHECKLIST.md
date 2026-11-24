# Post-Mint / Post-Claim Checklist

Run this after every mint, claim, or airdrop — it takes about a minute and
closes the most common leftover risks.

## 1. Confirm what you got

- [ ] Transaction confirmed on the block explorer (BscScan / Etherscan).
- [ ] Token / NFT balance matches what was promised.
- [ ] No second, unexpected transaction in your history.

## 2. Disconnect the site

- [ ] In your wallet, disconnect the dApp you just used.
- [ ] If the wallet shows a lingering session, disconnect it too.
- [ ] Keep a short allowlist of sites you deliberately stay connected to
      (for example, a project you mint/build on regularly). Everything else
      gets disconnected after use.

## 3. Check allowances

```bash
python3 src/check_allowances.py --config my-config.json --chain bsc
```

- [ ] Look for `UNLIMITED` allowances first.
- [ ] Note the spender address and label for each one.

## 4. Revoke what you no longer need

- [ ] Revoke unlimited approvals to one-off mint / claim contracts.
- [ ] Do **not** revoke an approval you still need — an open stake, a
      bridge in flight, or a position you manage through that spender.
      See `docs/REVOKE-GUIDE.md`.
- [ ] Build the revoke calldata locally if you like:
  ```bash
  python3 src/revoke_calldata.py --token <TOKEN> --spender <SPENDER>
  ```

## 5. Verify

- [ ] Re-run `check_allowances.py` and confirm the revoked allowance is `0`.
- [ ] Check the wallet's connected-sites list once more — the site you
      used should be gone.

## 6. Never

- [ ] Never share a seed phrase or private key — no legitimate revoke or
      support flow needs one.
- [ ] Never approve a transaction you did not preview: check the `to`
      address, the value, and what the call does before you sign.
