# Data Folder

The project does not commit large raw or processed data files.

## Raw data

`data/raw/` is populated by:

```powershell
python scripts/download_source_data.py
```

The script downloads UCI Online Retail II and extracts the source workbook.

## Processed data

`data/processed/` is populated by:

```powershell
python scripts/prepare_orders.py
python scripts/generate_extensions.py
python scripts/build_database.py
```

Generated outputs include cleaned order lines, product/market dimensions, profit facts, ad-spend facts, inventory facts, and a local SQLite database.

## Git policy

Raw and processed files are ignored because they are large and reproducible. Git tracks only scripts, SQL, documentation, profiles, validation summaries, and reports.

`data/sample/` is committed and contains small preview CSVs for GitHub reviewers.
