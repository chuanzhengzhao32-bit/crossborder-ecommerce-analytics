# Sample Data

This folder contains small preview CSVs exported from the generated processed tables. They exist so a GitHub reviewer can inspect table shape without downloading or rebuilding the full dataset.

The full dataset is not committed. Rebuild it with:

```powershell
python scripts/download_source_data.py
python scripts/prepare_orders.py
python scripts/generate_extensions.py
python scripts/build_database.py
```

Sample files are for structure preview only. Use the full generated tables for analysis.
