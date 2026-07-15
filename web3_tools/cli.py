"""web3-tools command line interface."""
import argparse
import sys
from typing import List, Optional

from web3_tools import __version__
from web3_tools.output import save_wallets
from web3_tools.wallet import generate_wallet

SECURITY_WARNING = (
    "WARNING: this file contains private keys and seed phrases in plaintext.\n"
    "Anyone with this file controls the wallets. Store it accordingly."
)


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return number


def _print_wallets(wallets) -> None:
    for index, wallet in enumerate(wallets, 1):
        print(f"Wallet {index}")
        print(f"  Address:     {wallet.address}")
        print(f"  Private key: {wallet.private_key}")
        if wallet.mnemonic:
            print(f"  Mnemonic:    {wallet.mnemonic}")


def _output_wallets(wallets, output: Optional[str]) -> None:
    if output:
        path = save_wallets(wallets, output)
        print(f"Saved {len(wallets)} wallet(s) to {path}")
        print(SECURITY_WARNING)
    else:
        _print_wallets(wallets)


def _cmd_generate(args: argparse.Namespace) -> int:
    wallets = [generate_wallet(with_mnemonic=args.mnemonic) for _ in range(args.number)]
    _output_wallets(wallets, args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web3-tools",
        description="Generate EVM wallets and find vanity addresses.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="generate random wallets")
    generate.add_argument("-n", "--number", type=_positive_int, default=1)
    generate.add_argument(
        "--mnemonic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="include a seed phrase (default: on)",
    )
    generate.add_argument("-o", "--output", help="output file (.csv or .json)")
    generate.set_defaults(func=_cmd_generate)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code or 0
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
