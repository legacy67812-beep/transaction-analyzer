"""Load raw transactions from a UTF-8 CSV file."""
import csv
from pathlib import Path
from typing import Any

def load_transactions(path: str | Path) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, restkey="__extra_columns__", restval=None)
        if reader.fieldnames is None:
            return []
        missing_columns = {"user", "amount", "status"} - set(reader.fieldnames)
        if missing_columns:
            raise ValueError("Missing required CSV columns: " + ", ".join(sorted(missing_columns)))
        return [dict(row) for row in reader]
