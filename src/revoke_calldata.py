#!/usr/bin/env python3
"""Build approve(spender, 0) calldata to revoke an ERC-20 allowance.

This script builds calldata only. It sends nothing, signs nothing, and asks
for no private key or seed phrase. Review the output, then send the
transaction yourself from your own wallet (or use a revoke site you trust).

Usage:
    python3 src/revoke_calldata.py \
        --token 0x55d398326f99059fF775485246999027B3197955 \
        --spender 0x10ED43C718714eb63d5aA57B78B54704E256024E

Output is the `data` field for a transaction whose `to` is the token
contract, with value 0.
"""

import argparse

APPROVE_SELECTOR = "095ea7b3"  # approve(address,uint256)


def build_calldata(spender, amount=0):
    spender_hex = spender.lower().replace("0x", "")
    return (
        "0x" + APPROVE_SELECTOR
        + "000000000000000000000000" + spender_hex
        + f"{amount:064x}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", required=True, help="ERC-20 token contract")
    parser.add_argument("--spender", required=True,
                        help="Spender to revoke approval from")
    parser.add_argument("--amount", type=int, default=0,
                        help="New allowance (default 0 = full revoke)")
    args = parser.parse_args()

    for name, value in (("token", args.token), ("spender", args.spender)):
        if not value.lower().startswith("0x") or len(value) != 42:
            parser.error(f"not a valid EVM address for --{name}: {value}")

    print(f"to:    {args.token}   (the token contract, value 0)")
    print(f"data:  {build_calldata(args.spender, args.amount)}")
    print(f"Effect: approve({args.spender}, {args.amount})")
    print("Send this from your own wallet. Re-run check_allowances.py")
    print("afterwards to confirm the allowance is now 0.")


if __name__ == "__main__":
    main()
