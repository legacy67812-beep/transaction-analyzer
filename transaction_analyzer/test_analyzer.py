"""Tests for validation and analysis."""
import copy
import math
import pytest
from .validator import validate_transaction
from .analyzer import analyze_transactions
from .types import AnalysisReport, ValidatedTransaction

def tx(user="alice", amount=10, status="success"):
    return {"user": user, "amount": amount, "status": status}

def test_valid_integer():
    assert validate_transaction(tx()) == {"user": "alice", "amount": 10.0}

def test_trim_user_and_numeric_string():
    assert validate_transaction(tx(" bob ", " 12.5 ")) == {"user": "bob", "amount": 12.5}

def test_failed_status():
    assert validate_transaction(tx(status="failed")) is None

def test_missing_user():
    assert validate_transaction({"amount": 5, "status": "success"}) is None

def test_blank_user():
    assert validate_transaction(tx("   ")) is None

def test_missing_amount():
    assert validate_transaction({"user": "alice", "status": "success"}) is None

@pytest.mark.parametrize("amount", [None, "abc", [], True, False, 0, -10, "-2", "nan", "inf", "-inf", float("nan"), float("inf"), float("-inf"), 10**1000])
def test_invalid_amount(amount):
    assert validate_transaction(tx(amount=amount)) is None

def test_empty_input():
    assert analyze_transactions([]) == {"users": {}, "valid_count": 0, "skipped_count": 0}

def test_aggregate_normalized_users():
    assert analyze_transactions([tx("bob", 10), tx(" bob ", "20")]) == {"users": {"bob": 30.0}, "valid_count": 2, "skipped_count": 0}

def test_skipped_once_per_record():
    assert analyze_transactions([tx("", -10), tx("alice", 3), tx("alice", 2, "failed")]) == {"users": {"alice": 3.0}, "valid_count": 1, "skipped_count": 2}

def test_original_input_unchanged():
    data = [tx(" alice ", "12.5"), tx("bob", None)]
    original = copy.deepcopy(data)
    analyze_transactions(data)
    assert data == original

def test_non_dictionary_record_is_skipped():
    assert analyze_transactions([None, tx("alice", 1)]) == {"users": {"alice": 1.0}, "valid_count": 1, "skipped_count": 1}

def test_aggregation_overflow_to_infinity():
    first = validate_transaction(tx("alice", 1e308))
    second = validate_transaction(tx("alice", 1e308))
    assert first is not None and second is not None
    assert math.isfinite(first["amount"]) and math.isfinite(second["amount"])
    report = analyze_transactions([tx("alice", 1e308), tx("alice", 1e308)])
    assert report["valid_count"] == 2 and report["skipped_count"] == 0
    assert math.isinf(report["users"]["alice"]) and report["users"]["alice"] > 0

def test_typed_dict_shapes():
    assert ValidatedTransaction.__required_keys__ == {"user", "amount"}
    assert AnalysisReport.__required_keys__ == {"users", "valid_count", "skipped_count"}
