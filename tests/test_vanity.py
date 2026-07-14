import pytest

from web3_tools.vanity import (
    Position,
    estimate_attempts,
    matches,
    normalize_pattern,
)

ADDR = "0xDeadBeef1234567890abcdef1234567890AbCafe"


def test_normalize_strips_0x_and_lowercases():
    assert normalize_pattern("0xDEAD") == "dead"


def test_normalize_without_0x():
    assert normalize_pattern("Cafe") == "cafe"


def test_normalize_rejects_non_hex():
    with pytest.raises(ValueError, match="non-hex"):
        normalize_pattern("xyz")


def test_normalize_rejects_empty():
    with pytest.raises(ValueError):
        normalize_pattern("0x")


def test_normalize_rejects_too_long():
    with pytest.raises(ValueError):
        normalize_pattern("a" * 41)


def test_matches_prefix_case_insensitive():
    # This exact case was broken in the old scripts:
    # uppercase pattern vs lowercased address never matched.
    assert matches(ADDR, normalize_pattern("0xDEADBEEF"), Position.PREFIX)


def test_matches_prefix_negative():
    assert not matches(ADDR, "cafe", Position.PREFIX)


def test_matches_suffix():
    assert matches(ADDR, "cafe", Position.SUFFIX)


def test_matches_anywhere():
    assert matches(ADDR, "567890", Position.ANYWHERE)


def test_matches_anywhere_negative():
    assert not matches(ADDR, "ffff", Position.ANYWHERE)


def test_estimate_prefix():
    assert estimate_attempts("dead", Position.PREFIX) == 16 ** 4


def test_estimate_anywhere_is_easier_than_prefix():
    assert estimate_attempts("dead", Position.ANYWHERE) < estimate_attempts(
        "dead", Position.PREFIX
    )
