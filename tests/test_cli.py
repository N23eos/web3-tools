import csv

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
