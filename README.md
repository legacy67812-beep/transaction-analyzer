# Transaction Analyzer

A Python CLI that reads CSV transactions, validates them, aggregates successful positive amounts per user, and saves a JSON report.

## Features

- Required CSV columns: `user`, `amount`, `status`; additional columns allowed.
- Skips invalid transactions and reports valid/skipped counts.
- Trims usernames, supports UTF-8 and Cyrillic text.
- Saves readable JSON, rejecting non-finite totals.
- Includes pytest tests.

## Requirements and installation

Python 3.10+. From the repository root:

```powershell
python -m pip install pytest
```

## Run

```powershell
python -m transaction_analyzer.main transaction_analyzer/transactions.csv report.json
```

Example CSV:

```csv
user,amount,status
alice,100,success
bob,50,failed
alice,200,success
```

## Tests

```powershell
python -m pytest transaction_analyzer -v
```

**Note:** Amounts use `float`, not exact decimal arithmetic. This tool is educational and not intended for precision financial accounting.
