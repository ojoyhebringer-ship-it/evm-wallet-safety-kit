# Chains

Default chains in `src/check_allowances.py`. You can override the RPC URL
per run with `--rpc-url` or per config with `"rpc_url"`.

| Key | Chain | Chain ID | Default public RPC |
| --- | --- | --- | --- |
| `bsc` | BNB Smart Chain | 56 | https://bsc-dataseed.binance.org/ |
| `ethereum` | Ethereum | 1 | https://eth.llamarpc.com |
| `robinhood` | Robinhood Chain | 4663 | https://mainnet.rpc.therobinhoodchain.com |
| `sepolia` | Sepolia (testnet) | 11155159 | https://ethereum-sepolia-rpc.publicnode.com |

Public RPCs can be slow or rate-limited. If a check fails, retry once, or
point the script at an RPC you run or trust.
