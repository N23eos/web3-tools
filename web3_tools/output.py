"""Save wallets to CSV or JSON, chosen by file extension."""
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Union

from web3_tools.wallet import Wallet

FIELDS = ("address", "private_key", "mnemonic")
SUPPORTED_EXTENSIONS = (".csv", ".json")


def save_wallets(wallets: Iterable[Wallet], path: Union[str, Path]) -> Path:
    path = Path(path)
    rows = [asdict(wallet) for wallet in wallets]
    if path.suffix == ".csv":
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row[key] or "" for key in FIELDS})
    elif path.suffix == ".json":
        path.write_text(json.dumps(rows, indent=2))
    else:
        raise ValueError(
            f"Unsupported output format '{path.suffix}': "
            f"use {' or '.join(SUPPORTED_EXTENSIONS)}"
        )
    return path
