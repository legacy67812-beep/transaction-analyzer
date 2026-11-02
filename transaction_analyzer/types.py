from typing import TypedDict

class ValidatedTransaction(TypedDict):
    user: str
    amount: float

class AnalysisReport(TypedDict):
    users: dict[str, float]
    valid_count: int
    skipped_count: int
