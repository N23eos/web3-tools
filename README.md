# Wallet Pattern Finder Scripts

This repository contains Python scripts for generating cryptocurrency wallets and finding addresses that match specific patterns. Ideal for developers and crypto enthusiasts exploring custom wallet patterns.

---

## Script Descriptions

### 1. `wallets-creator.py`
Generates random cryptocurrency wallets (public/private key pairs).

#### Usage:
- Run the script to create wallets.
- Outputs wallet addresses with their private keys.

---

### 2. `wallet-pattern-creator.py`
Finds wallets that match specific patterns in their addresses.

#### Usage:
1. Add patterns to the `PATTERNS` list in the script (e.g., `"0xABCDEF"`).
2. Run:
   ```bash
   python wallet-pattern-creator.py
