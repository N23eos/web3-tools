from eth_account import Account

from web3_tools.wallet import Wallet, generate_wallet


def test_generate_wallet_returns_valid_checksum_address():
    wallet = generate_wallet()
    assert wallet.address.startswith("0x")
    assert len(wallet.address) == 42
    # eth-account returns checksummed addresses
    assert wallet.address == Account.from_key(wallet.private_key).address


def test_generate_wallet_without_mnemonic_by_default():
    wallet = generate_wallet()
    assert wallet.mnemonic is None


def test_generate_wallet_with_mnemonic():
    wallet = generate_wallet(with_mnemonic=True)
    assert wallet.mnemonic is not None
    assert len(wallet.mnemonic.split()) in (12, 15, 18, 21, 24)


def test_private_key_is_hex_string():
    wallet = generate_wallet()
    assert wallet.private_key.startswith("0x")
    int(wallet.private_key, 16)  # raises if not hex


def test_wallets_are_unique():
    a, b = generate_wallet(), generate_wallet()
    assert a.address != b.address
