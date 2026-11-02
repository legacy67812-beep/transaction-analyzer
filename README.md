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


## Структура проекта

Основные файлы находятся в каталоге `transaction_analyzer/`:

- `main.py` — точка входа CLI: принимает пути к CSV и JSON, запускает обработку и сообщает об ошибках.
- `csv_loader.py` — читает CSV и проверяет наличие обязательных столбцов `user`, `amount`, `status`.
- `validator.py` — проверяет отдельную транзакцию и нормализует имя пользователя и сумму.
- `analyzer.py` — суммирует успешные транзакции по пользователям и считает принятые и пропущенные записи.
- `report_writer.py` — сохраняет результат в JSON с поддержкой Unicode.
- `types.py` — описывает структуры данных через `TypedDict`.
- `test_analyzer.py` — тесты валидации и агрегации.
- `test_csv.py` — тесты загрузки CSV, формата заголовков, записи JSON и CLI.
- `transactions.csv` — пример входных данных.

## Tests

```powershell
python -m pytest transaction_analyzer -v
```

**Note:** Amounts use `float`, not exact decimal arithmetic. This tool is educational and not intended for precision financial accounting.
