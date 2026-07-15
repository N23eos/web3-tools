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


from web3_tools.vanity import search


def test_search_finds_single_char_pattern_quickly():
    # 1 hex char = 1/16 odds per attempt; finds in well under a second
    wallets = search(
        pattern="a",
        position=Position.PREFIX,
        count=2,
        workers=2,
    )
    assert len(wallets) == 2
    for wallet in wallets:
        assert wallet.address.lower()[2:].startswith("a")
        assert wallet.mnemonic is None


def test_search_with_mnemonic():
    wallets = search(
        pattern="a",
        position=Position.PREFIX,
        count=1,
        workers=1,
        with_mnemonic=True,
    )
    assert wallets[0].mnemonic is not None


def test_matches_accepts_unnormalized_pattern():
    assert matches(ADDR, "0xDEAD", Position.PREFIX)
