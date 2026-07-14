import csv
import json

import pytest

from web3_tools.output import save_wallets
from web3_tools.wallet import Wallet

WALLETS = [
    Wallet("0xAbc", "0x111", "word one two"),
    Wallet("0xDef", "0x222", None),
]


def test_save_csv_roundtrip(tmp_path):
    path = tmp_path / "wallets.csv"
    save_wallets(WALLETS, path)
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["address"] == "0xAbc"
    assert rows[0]["mnemonic"] == "word one two"
    assert rows[1]["private_key"] == "0x222"
    assert rows[1]["mnemonic"] == ""


def test_save_json_roundtrip(tmp_path):
    path = tmp_path / "wallets.json"
    save_wallets(WALLETS, path)
    data = json.loads(path.read_text())
    assert data[0]["address"] == "0xAbc"
    assert data[1]["mnemonic"] is None


def test_unknown_extension_rejected(tmp_path):
    with pytest.raises(ValueError, match="csv or .json"):
        save_wallets(WALLETS, tmp_path / "wallets.xlsx")
