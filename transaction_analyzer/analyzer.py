"""Aggregation of validated transactions."""
from typing import Any
from .types import AnalysisReport
from .validator import validate_transaction

def analyze_transactions(transactions: list[dict[str, Any]]) -> AnalysisReport:
    users: dict[str, float] = {}
    valid_count = skipped_count = 0
    for transaction in transactions:
        validated = validate_transaction(transaction)
        if validated is None:
            skipped_count += 1
            continue
        user, amount = validated["user"], validated["amount"]
        users[user] = users.get(user, 0.0) + amount
        valid_count += 1
    return {"users": users, "valid_count": valid_count, "skipped_count": skipped_count}
