"""Save an analysis report to JSON using UTF-8."""
import json
from pathlib import Path
from .types import AnalysisReport

def save_report(report: AnalysisReport, path: str | Path) -> None:
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    with open(path, "w", encoding="utf-8") as file:
        file.write(payload + "\n")
