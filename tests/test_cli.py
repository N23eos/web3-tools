import csv
import json

from web3_tools.cli import main


def test_generate_to_csv(tmp_path, capsys):
    out = tmp_path / "wallets.csv"
    exit_code = main(["generate", "-n", "3", "-o", str(out)])
    assert exit_code == 0
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert all(row["mnemonic"] for row in rows)  # mnemonic on by default
    captured = capsys.readouterr()
    assert "WARNING" in captured.out  # plaintext keys warning


def test_generate_no_mnemonic(tmp_path):
    out = tmp_path / "wallets.csv"
    main(["generate", "-n", "1", "--no-mnemonic", "-o", str(out)])
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["mnemonic"] == ""


def test_generate_prints_to_stdout_without_output_file(capsys):
    exit_code = main(["generate", "-n", "1"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "0x" in captured.out


def test_invalid_count_rejected(capsys):
    exit_code = main(["generate", "-n", "0"])
    assert exit_code == 2


def test_vanity_finds_and_saves(tmp_path):
    out = tmp_path / "found.json"
    exit_code = main(
        ["vanity", "a", "--count", "1", "--workers", "1", "-o", str(out), "--yes"]
    )
    assert exit_code == 0
    data = json.loads(out.read_text())
    assert len(data) == 1
    assert data[0]["address"].lower()[2:].startswith("a")


def test_vanity_rejects_bad_pattern(capsys):
    exit_code = main(["vanity", "xyz"])
    assert exit_code == 1
    assert "non-hex" in capsys.readouterr().err


def test_vanity_rejects_bad_output_extension_before_search(capsys):
    exit_code = main(["vanity", "a", "-o", "out.xlsx", "--yes"])
    assert exit_code == 1
    assert "csv or .json" in capsys.readouterr().err


def test_vanity_hard_pattern_requires_confirmation(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    exit_code = main(["vanity", "aaaaaaaa", "--count", "1"])
    assert exit_code == 0
    assert "Aborted" in capsys.readouterr().out


def test_vanity_unwritable_output_dir_fails_before_search(capsys):
    exit_code = main(
        ["vanity", "a", "-o", "/nonexistent_dir_xyz/out.csv", "--yes"]
    )
    assert exit_code == 1
    assert "Cannot write" in capsys.readouterr().err


def test_generate_prints_wallets_when_save_fails(tmp_path, monkeypatch, capsys):
    import web3_tools.cli as cli

    def fail_save(wallets, path):
        raise OSError("disk full")

    monkeypatch.setattr(cli, "save_wallets", fail_save)
    exit_code = main(["generate", "-n", "1", "-o", str(tmp_path / "w.csv")])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "disk full" in captured.err
    assert "0x" in captured.out  # keys printed, not lost


def test_vanity_confirmation_eof_aborts(monkeypatch, capsys):
    def raise_eof(prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    exit_code = main(["vanity", "aaaaaaaa", "--count", "1"])
    assert exit_code == 0
    assert "Aborted" in capsys.readouterr().out


def test_vanity_removes_precreated_file_when_nothing_found(tmp_path, monkeypatch):
    import web3_tools.cli as cli

    out = tmp_path / "found.csv"
    monkeypatch.setattr(cli, "search", lambda **kwargs: [])
    exit_code = main(["vanity", "a", "-o", str(out), "--yes"])
    assert exit_code == 1
    assert not out.exists()  # pre-flight placeholder cleaned up


def test_vanity_keeps_existing_file_when_nothing_found(tmp_path, monkeypatch):
    import web3_tools.cli as cli

    out = tmp_path / "found.csv"
    out.write_text("existing data")
    monkeypatch.setattr(cli, "search", lambda **kwargs: [])
    exit_code = main(["vanity", "a", "-o", str(out), "--yes"])
    assert exit_code == 1
    assert out.read_text() == "existing data"


def test_generate_unwritable_output_dir_fails_fast(capsys):
    exit_code = main(["generate", "-n", "1", "-o", "/nonexistent_dir_xyz/w.csv"])
    assert exit_code == 1
    assert "Cannot write" in capsys.readouterr().err
