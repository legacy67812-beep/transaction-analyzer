"""Validation and normalization of individual transactions."""
import math
from typing import Any
from .types import ValidatedTransaction

def validate_transaction(transaction: Any) -> ValidatedTransaction | None:
    if not isinstance(transaction, dict) or transaction.get("status") != "success":
        return None
    user = transaction.get("user")
    if not isinstance(user, str) or not user.strip():
        return None
    amount = transaction.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float, str)):
        return None
    try:
        normalized_amount = float(amount)
    except (ValueError, TypeError, OverflowError):
        return None
    if not math.isfinite(normalized_amount) or normalized_amount <= 0:
        return None
    return {"user": user.strip(), "amount": normalized_amount}
