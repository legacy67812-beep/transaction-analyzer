"""CLI: python -m transaction_analyzer.main INPUT.csv OUTPUT.json"""
import argparse
import csv
import sys
from .analyzer import analyze_transactions
from .csv_loader import load_transactions
from .report_writer import save_report

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze CSV transactions and save JSON report")
    parser.add_argument("input_csv")
    parser.add_argument("output_json")
    args = parser.parse_args(argv)
    try:
        report = analyze_transactions(load_transactions(args.input_csv))
        save_report(report, args.output_json)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Saved report to {args.output_json}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
