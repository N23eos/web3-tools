"""EVM wallet generation."""
from dataclasses import dataclass
from typing import Optional

from eth_account import Account

Account.enable_unaudited_hdwallet_features()


@dataclass(frozen=True)
class Wallet:
    address: str
    private_key: str
    mnemonic: Optional[str] = None


def _key_hex(key: bytes) -> str:
    # eth-account < 0.9 returns hex without 0x prefix; normalize
    hex_key = key.hex()
    return hex_key if hex_key.startswith("0x") else "0x" + hex_key


def generate_wallet(with_mnemonic: bool = False) -> Wallet:
    """Generate a new random EVM wallet.

    Raw key generation (default) is ~10x faster than mnemonic generation,
    which matters for vanity search.
    """
    if with_mnemonic:
        account, mnemonic = Account.create_with_mnemonic()
        return Wallet(account.address, _key_hex(account.key), mnemonic)
    account = Account.create()
    return Wallet(account.address, _key_hex(account.key))
