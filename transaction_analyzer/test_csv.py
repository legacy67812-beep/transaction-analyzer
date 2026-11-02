"""CSV integration and JSON output tests."""
import json
import math
import subprocess
import sys
from pathlib import Path
import pytest
from .analyzer import analyze_transactions
from .csv_loader import load_transactions
from .main import main
from .report_writer import save_report

def test_example_csv(tmp_path):
    path = tmp_path / "transactions.csv"
    path.write_text("user,amount,status\nalice,100,success\nbob,50,failed\nalice,200,success\ncharlie,abc,success\nbob,75,success\n", encoding="utf-8")
    assert analyze_transactions(load_transactions(path)) == {"users": {"alice": 300.0, "bob": 75.0}, "valid_count": 3, "skipped_count": 2}

def test_empty_csv(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    assert load_transactions(path) == []
    assert analyze_transactions(load_transactions(path))["valid_count"] == 0

def test_header_only_csv(tmp_path):
    path = tmp_path / "header.csv"
    path.write_text("user,amount,status\n", encoding="utf-8")
    assert load_transactions(path) == []

def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_transactions(tmp_path / "missing.csv")

def test_invalid_amount_is_skipped_not_crash(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_text("user,amount,status\nalice,abc,success\nbob,5,success\n", encoding="utf-8")
    assert analyze_transactions(load_transactions(path)) == {"users": {"bob": 5.0}, "valid_count": 1, "skipped_count": 1}

def test_missing_fields_and_extra_columns(tmp_path):
    path = tmp_path / "malformed.csv"
    path.write_text("user,amount,status\nalice,10\nbob,5,success,unexpected\ncharlie,7,success\n", encoding="utf-8")
    rows = load_transactions(path)
    assert len(rows) == 3
    assert rows[1]["__extra_columns__"] == ["unexpected"]
    report = analyze_transactions(rows)
    assert report["valid_count"] == 2 and report["skipped_count"] == 1

def test_russian_names_and_utf8_json(tmp_path):
    csv_path = tmp_path / "russian.csv"
    json_path = tmp_path / "result.json"
    csv_path.write_text("user,amount,status\n Иван ,12.5,success\nИван,7.5,success\n", encoding="utf-8")
    save_report(analyze_transactions(load_transactions(csv_path)), json_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["users"] == {"Иван": 20.0}
    assert "Иван" in json_path.read_text(encoding="utf-8")

def test_utf8_bom(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_text("user,amount,status\nОльга,5,success\n", encoding="utf-8-sig")
    assert analyze_transactions(load_transactions(path))["users"] == {"Ольга": 5.0}

def test_bad_encoding(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"user,amount,status\n\xff,5,success\n")
    with pytest.raises(UnicodeDecodeError):
        load_transactions(path)

def test_cli_saves_json(tmp_path):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.json"
    source.write_text("user,amount,status\nАня,8,success\n", encoding="utf-8")
    assert main([str(source), str(target)]) == 0
    assert json.loads(target.read_text(encoding="utf-8"))["users"] == {"Аня": 8.0}

def test_cli_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "absent.csv"), str(tmp_path / "out.json")]) == 1
    assert "Error:" in capsys.readouterr().err

def test_writer_rejects_infinite_aggregate(tmp_path):
    path = tmp_path / "report.json"
    report = analyze_transactions([{"user": "alice", "amount": 1e308, "status": "success"}, {"user": "alice", "amount": 1e308, "status": "success"}])
    assert math.isinf(report["users"]["alice"])
    with pytest.raises(ValueError):
        save_report(report, path)
    assert not path.exists()

def test_module_invocation_from_parent(tmp_path):
    package_parent = Path(__file__).resolve().parent.parent
    csv_path = tmp_path / "input.csv"
    output = tmp_path / "output.json"
    csv_path.write_text("user,amount,status\nbob,3,success\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "transaction_analyzer.main", str(csv_path), str(output)], cwd=package_parent, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["users"] == {"bob": 3.0}

def test_csv_schema_accepts_required_headers(tmp_path):
    path = tmp_path / "valid_headers.csv"
    path.write_text("user,amount,status\nalice,10,success\n", encoding="utf-8")
    assert load_transactions(path) == [{"user": "alice", "amount": "10", "status": "success"}]

def test_csv_schema_rejects_missing_amount_header(tmp_path):
    path = tmp_path / "missing_amount.csv"
    path.write_text("user,price,status\nalice,10,success\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required CSV columns: amount"):
        load_transactions(path)

def test_csv_schema_rejects_multiple_missing_headers(tmp_path):
    path = tmp_path / "missing_multiple.csv"
    path.write_text("user,price\nalice,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="amount, status"):
        load_transactions(path)

def test_csv_schema_allows_extra_headers(tmp_path):
    path = tmp_path / "extra_header.csv"
    path.write_text("user,amount,status,note\nИван,5,success,ok\n", encoding="utf-8")
    rows = load_transactions(path)
    assert rows[0]["note"] == "ok"
    assert analyze_transactions(rows)["users"] == {"Иван": 5.0}

def test_csv_schema_rejects_header_only_missing_required_column(tmp_path):
    path = tmp_path / "header_only_invalid.csv"
    path.write_text("user,status\n", encoding="utf-8")
    with pytest.raises(ValueError, match="amount"):
        load_transactions(path)
