"""Vanity address pattern matching and parallel search."""
from enum import Enum

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
