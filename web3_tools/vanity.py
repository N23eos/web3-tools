"""Vanity address pattern matching and parallel search."""
import multiprocessing
import queue as queue_module
from enum import Enum
from typing import Callable, List, Optional

from web3_tools.wallet import Wallet, generate_wallet

HEX_CHARS = frozenset("0123456789abcdef")
ADDRESS_HEX_LENGTH = 40  # address length without the 0x prefix


class Position(str, Enum):
    PREFIX = "prefix"
    SUFFIX = "suffix"
    ANYWHERE = "anywhere"


def normalize_pattern(pattern: str) -> str:
    """Lowercase, strip optional 0x, validate hex-only and length."""
    normalized = pattern.lower()
    if normalized.startswith("0x"):
        normalized = normalized[2:]
    if not normalized:
        raise ValueError("Pattern is empty")
    if len(normalized) > ADDRESS_HEX_LENGTH:
        raise ValueError(
            f"Pattern longer than {ADDRESS_HEX_LENGTH} hex chars can never match"
        )
    invalid = set(normalized) - HEX_CHARS
    if invalid:
        raise ValueError(
            f"Pattern contains non-hex characters: {', '.join(sorted(invalid))}. "
            "Addresses only contain 0-9 and a-f."
        )
    return normalized


def matches(address: str, pattern: str, position: Position) -> bool:
    """Case-insensitive match of a normalized pattern against an address."""
    body = address.lower()[2:]  # strip 0x
    if position is Position.PREFIX:
        return body.startswith(pattern)
    if position is Position.SUFFIX:
        return body.endswith(pattern)
    return pattern in body


def estimate_attempts(pattern: str, position: Position) -> int:
    """Expected number of random addresses to try before a match."""
    base = 16 ** len(pattern)
    if position is Position.ANYWHERE:
        slots = ADDRESS_HEX_LENGTH - len(pattern) + 1
        return max(1, base // slots)
    return base


PROGRESS_POLL_SECONDS = 1.0


def _worker(
    pattern: str,
    position: Position,
    with_mnemonic: bool,
    found_queue: "multiprocessing.Queue",
    stop_event: "multiprocessing.synchronize.Event",
    attempts: "multiprocessing.sharedctypes.Synchronized",
) -> None:
    try:
        while not stop_event.is_set():
            wallet = generate_wallet(with_mnemonic)
            with attempts.get_lock():
                attempts.value += 1
            if matches(wallet.address, pattern, position):
                found_queue.put(wallet)
    except KeyboardInterrupt:
        return  # parent handles shutdown; don't spew a traceback per worker


def search(
    pattern: str,
    position: Position,
    count: int = 1,
    workers: int = 1,
    with_mnemonic: bool = False,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> List[Wallet]:
    """Search for `count` wallets matching `pattern` using worker processes.

    `on_progress(attempts, found)` is called roughly once per second.
    Returns found wallets; on KeyboardInterrupt returns what was found so far.
    """
    found_queue: multiprocessing.Queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    attempts = multiprocessing.Value("Q", 0)

    processes = [
        multiprocessing.Process(
            target=_worker,
            args=(pattern, position, with_mnemonic, found_queue, stop_event, attempts),
            daemon=True,
        )
        for _ in range(workers)
    ]
    for process in processes:
        process.start()

    found: List[Wallet] = []
    try:
        while len(found) < count:
            try:
                wallet = found_queue.get(timeout=PROGRESS_POLL_SECONDS)
                found.append(wallet)
            except queue_module.Empty:
                if not any(process.is_alive() for process in processes):
                    break
            if on_progress is not None:
                on_progress(attempts.value, len(found))
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        for process in processes:
            process.join(timeout=2)
            if process.is_alive():
                process.terminate()
    return found
