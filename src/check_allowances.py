#!/usr/bin/env python3
"""Check ERC-20 allowances for an EVM wallet. Read-only, stdlib only.

Reads allowance(owner, spender) and balanceOf(owner) via eth_call against a
public RPC. Sends no transactions, asks for no private key or seed phrase.

Usage:
    python3 src/check_allowances.py --config my-config.json --chain bsc
    python3 src/check_allowances.py --wallet 0x... --chain bsc \
        --token 0x55d398326f99059fF775485246999027B3197955:USDT \
        --spender 0x10ED43C718714eb63d5aA57B78B54704E256024E:PancakeSwapRouter

Config file format (see examples/config.example.json):
    {
      "wallet": "0x...",
      "chain": "bsc",
      "tokens": [{"address": "0x...", "label": "USDT"}],
      "spenders": [{"address": "0x...", "label": "Example Mint"}]
    }
"""

import argparse
import json
import sys
import urllib.request

# Selectors for the ERC-20 functions we call (first 4 bytes of keccak256).
ALLOWANCE_SELECTOR = "dd62ed3e"  # allowance(address,address)
BALANCE_SELECTOR = "70a08231"    # balanceOf(address)
DECIMALS_SELECTOR = "313ce567"   # decimals()
SYMBOL_SELECTOR = "95d89b41"     # symbol()

CHAINS = {
    "bsc": {
        "id": 56,
        "name": "BNB Smart Chain",
        "rpc_url": "https://bsc-dataseed.binance.org/",
    },
    "ethereum": {
        "id": 1,
        "name": "Ethereum",
        "rpc_url": "https://eth.llamarpc.com",
    },
    "robinhood": {
        "id": 4663,
        "name": "Robinhood Chain",
        "rpc_url": "https://mainnet.rpc.therobinhoodchain.com",
    },
    "sepolia": {
        "id": 11155159,
        "name": "Sepolia",
        "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
    },
}

MAX_UINT256 = 2 ** 256 - 1


def rpc_call(rpc_url, method, params):
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    req = urllib.request.Request(
        rpc_url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def eth_call(rpc_url, to_address, calldata):
    return rpc_call(
        rpc_url, "eth_call", [{"to": to_address, "data": calldata}, "latest"]
    )


def pad_address(address):
    return "000000000000000000000000" + address.lower().replace("0x", "")


def parse_uint(hex_value):
    if not hex_value or hex_value == "0x":
        return 0
    return int(hex_value, 16)


def parse_string(hex_value):
    """Decode an ABI-encoded string return value (best effort)."""
    if not hex_value or hex_value == "0x":
        return ""
    raw = bytes.fromhex(hex_value[2:])
    try:
        # string: offset (32) + length (32) + data
        length = int.from_bytes(raw[32:64], "big")
        return raw[64:64 + length].decode("utf-8", errors="replace")
    except Exception:
        return ""


def format_amount(raw, decimals):
    if decimals == 0:
        return str(raw)
    whole, frac = divmod(raw, 10 ** decimals)
    return f"{whole}.{frac:0{decimals}d}".rstrip("0").rstrip(".")


def short(address):
    return f"{address[:6]}...{address[-4:]}" if len(address) > 12 else address


def check_token(rpc_url, wallet, token, spenders):
    address = token["address"]
    label = token.get("label") or short(address)

    decimals = parse_uint(eth_call(rpc_url, address, "0x" + DECIMALS_SELECTOR))
    symbol = parse_string(eth_call(rpc_url, address, "0x" + SYMBOL_SELECTOR)) or label
    balance = parse_uint(
        eth_call(rpc_url, address, "0x" + BALANCE_SELECTOR + pad_address(wallet))
    )

    print(f"Token {symbol} ({decimals} decimals)  balance: "
          f"{format_amount(balance, decimals)}")
    for spender in spenders:
        spender_addr = spender["address"]
        spender_label = spender.get("label") or short(spender_addr)
        allowance = parse_uint(
            eth_call(
                rpc_url,
                address,
                "0x" + ALLOWANCE_SELECTOR
                + pad_address(wallet)
                + pad_address(spender_addr),
            )
        )
        if allowance == MAX_UINT256:
            status = "UNLIMITED (2**256-1)  <-- review"
        elif allowance == 0:
            status = "0"
        else:
            status = format_amount(allowance, decimals)
        print(f"  spender {short(spender_addr)} ({spender_label})"
              f"  allowance: {status}")
    print()


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="JSON config file")
    parser.add_argument("--wallet", help="Wallet address to check")
    parser.add_argument("--chain", default="bsc",
                        choices=sorted(CHAINS),
                        help="Chain key (default: bsc)")
    parser.add_argument("--rpc-url", help="Override the default RPC URL")
    parser.add_argument("--token", action="append", default=[],
                        help="TOKEN_ADDRESS[:LABEL], repeatable")
    parser.add_argument("--spender", action="append", default=[],
                        help="SPENDER_ADDRESS[:LABEL], repeatable")
    args = parser.parse_args(argv)

    config = load_config(args.config) if args.config else {}
    wallet = args.wallet or config.get("wallet")
    if not wallet:
        parser.error("wallet address is required (--wallet or config wallet)")
    if not wallet.lower().startswith("0x") or len(wallet) != 42:
        parser.error(f"not a valid EVM address: {wallet}")

    chain_key = args.chain or config.get("chain", "bsc")
    chain = CHAINS[chain_key]
    rpc_url = args.rpc_url or config.get("rpc_url") or chain["rpc_url"]

    tokens = list(config.get("tokens", []))
    for item in args.token:
        address, _, label = item.partition(":")
        tokens.append({"address": address, "label": label})
    spenders = list(config.get("spenders", []))
    for item in args.spender:
        address, _, label = item.partition(":")
        spenders.append({"address": address, "label": label})
    if not tokens:
        parser.error("at least one token is required")
    if not spenders:
        parser.error("at least one spender is required")

    print(f"Chain: {chain['name']} ({chain['id']})  Wallet: {short(wallet)}")
    print(f"RPC: {rpc_url}")
    print()
    for token in tokens:
        try:
            check_token(rpc_url, wallet, token, spenders)
        except Exception as exc:  # keep checking the other tokens
            print(f"Token {token.get('label') or token['address']}: ERROR: {exc}\n",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
