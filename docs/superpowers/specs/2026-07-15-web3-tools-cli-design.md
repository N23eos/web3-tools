# web3-tools CLI — Design

Date: 2026-07-15
Status: approved

## Goal

Replace 4 copy-pasted wallet scripts with a single installable CLI tool (`web3-tools`)
that generates EVM wallets and finds vanity addresses. Make the repo useful for other
people: pip-installable, documented, tested, with bugs fixed.

## Scope

- EVM only (one address works on Ethereum, Base, Arbitrum, BSC, etc.)
- Output: CSV and JSON (pandas/openpyxl removed)
- Old scripts (`wallets-creator.py`, `wallet-pattern-creator.py`,
  `wallets-pattern-until-find-anywhere.py`, `wallets-pattern-until-find-beginning.py`)
  are deleted — the CLI replaces them.

## Bugs in the old scripts this design fixes

1. **Case mismatch**: `address.lower().startswith("0xABCDEF")` — uppercase patterns
   never matched. Fix: normalize both sides to lowercase.
2. **"anywhere" script lied**: used `startswith`, never searched mid-address.
   Fix: explicit `--position prefix|suffix|anywhere`.
3. **Threads for CPU-bound work**: GIL made 4 threads no faster than 1, plus data race
   on a shared list. Fix: `multiprocessing`.
4. **Slow generation**: `create_with_mnemonic()` used even when only the address
   matters. Fix: raw key generation by default, `--mnemonic` flag opts back in.

## Architecture

```
web3-tools/
├── web3_tools/
│   ├── __init__.py     # version
│   ├── cli.py          # argparse parser, subcommands, entry point
│   ├── wallet.py       # wallet generation via eth-account
│   ├── vanity.py       # pattern matching + multiprocessing search
│   └── output.py       # CSV / JSON writers
├── tests/
│   ├── test_wallet.py
│   ├── test_vanity.py
│   └── test_output.py
├── pyproject.toml      # deps: eth-account; console_script `web3-tools`
├── requirements.txt    # kept as thin pointer for non-pip-install users
├── README.md           # English, usage examples, security warning
└── assets/readme-header.png
```

### Module contracts

**wallet.py**
- `generate_wallet(with_mnemonic: bool) -> Wallet` — frozen dataclass
  `Wallet(address, private_key, mnemonic | None)`.
- Raw mode: `Account.create()`. Mnemonic mode: `Account.create_with_mnemonic()`
  (requires `Account.enable_unaudited_hdwallet_features()` once).

**vanity.py**
- `matches(address: str, pattern: str, position: Position) -> bool` — pure function,
  case-insensitive, position = PREFIX | SUFFIX | ANYWHERE. Prefix compares against
  address without the `0x` prefix.
- `estimate_attempts(pattern: str, position: Position) -> int` — expected attempts
  (16^len for prefix/suffix; adjusted for anywhere).
- `search(pattern, position, count, workers, with_mnemonic, on_found) -> list[Wallet]`
  — spawns worker processes, each generates+checks in a loop, found wallets flow back
  through a `multiprocessing.Queue`; parent collects until `count` reached, then
  terminates workers. Ctrl+C saves what was found.
- Pattern validation: hex chars only (after stripping optional `0x`), fail fast with
  clear message.

**output.py**
- `save_wallets(wallets, path)` — format by extension (`.csv` → csv module,
  `.json` → json module). Unknown extension → error.

**cli.py**
- `web3-tools generate -n N [--mnemonic/--no-mnemonic (default on)] [-o FILE]`
- `web3-tools vanity PATTERN [--position prefix|suffix|anywhere] [--count N]
  [--workers N (default cpu_count)] [--mnemonic] [-o FILE]`
- Before search: print difficulty estimate; if expected attempts > ~16^7, warn that
  it may take very long and ask for confirmation (`--yes` skips).
- After any file write: print security warning (private keys in plaintext).

## Error handling

- Invalid pattern (non-hex) → exit with message before any work.
- Ctrl+C during vanity search → save found wallets (if `-o` given), print summary.
- Unwritable output path → fail before starting the search, not after.

## Testing

pytest. Unit tests for: `matches` (all positions, case-insensitivity, `0x` handling),
`estimate_attempts`, `save_wallets` (csv/json round-trip), `generate_wallet`
(address checksum validity, key ↔ address correspondence). Search smoke test with a
1-char pattern (finds fast). No network needed anywhere.

## README

English. Sections: what it is, install (`pip install .`), usage examples per command,
how vanity difficulty scales (table: pattern length → expected attempts), security
warning (plaintext keys, generated wallets are as safe as your machine), donate badge
kept.
