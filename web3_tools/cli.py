"""web3-tools command line interface."""
import argparse
import os
import sys
from typing import List, Optional

from web3_tools import __version__
from web3_tools.output import save_wallets
from web3_tools.vanity import Position, estimate_attempts, normalize_pattern, search
from web3_tools.wallet import generate_wallet

SECURITY_WARNING = (
    "WARNING: this file contains private keys and seed phrases in plaintext.\n"
    "Anyone with this file controls the wallets. Store it accordingly."
)

HARD_PATTERN_THRESHOLD = 16 ** 7  # ~268M expected attempts: hours of CPU time


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


def _cmd_vanity(args: argparse.Namespace) -> int:
    pattern = normalize_pattern(args.pattern)
    position = Position(args.position)

    # Fail on a bad output path now, not after hours of searching
    if args.output and not args.output.endswith((".csv", ".json")):
        raise ValueError(
            f"Unsupported output format '{args.output}': use .csv or .json"
        )

    expected = estimate_attempts(pattern, position)
    print(f"Pattern '{pattern}' ({position.value}): ~{expected:,} attempts per match expected")
    if expected > HARD_PATTERN_THRESHOLD and not args.yes:
        answer = input("This may take a very long time. Continue? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return 0

    def report_progress(attempts: int, found: int) -> None:
        print(f"\rAttempts: {attempts:,}  Found: {found}/{args.count}", end="", flush=True)

    wallets = search(
        pattern=pattern,
        position=position,
        count=args.count,
        workers=args.workers,
        with_mnemonic=args.mnemonic,
        on_progress=report_progress,
    )
    print()
    if not wallets:
        print("No wallets found (interrupted).")
        return 1
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

    vanity = subparsers.add_parser("vanity", help="find addresses matching a pattern")
    vanity.add_argument("pattern", help="hex pattern, e.g. dead or 0xCAFE")
    vanity.add_argument(
        "--position",
        choices=[p.value for p in Position],
        default=Position.PREFIX.value,
        help="where the pattern must appear (default: prefix)",
    )
    vanity.add_argument("--count", type=_positive_int, default=1)
    vanity.add_argument(
        "--workers", type=_positive_int, default=os.cpu_count() or 1,
        help="parallel processes (default: CPU count)",
    )
    vanity.add_argument(
        "--mnemonic", action="store_true",
        help="generate wallets with seed phrases (slower search)",
    )
    vanity.add_argument("--yes", action="store_true", help="skip difficulty confirmation")
    vanity.add_argument("-o", "--output", help="output file (.csv or .json)")
    vanity.set_defaults(func=_cmd_vanity)

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
