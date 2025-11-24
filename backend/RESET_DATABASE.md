# Reset and Import Database

Quick guide to wipe and repopulate the database with `testing2.csv`.

## One-Command Reset and Import

```bash
cd backend
python reset_and_import.py
```

This will:
1. ✅ Delete `riskchain.db` (if it exists)
2. ✅ Initialize a fresh database
3. ✅ Import all data from `testing2.csv`

## Custom Options

```bash
# Use a different CSV file
python reset_and_import.py my_data.csv

# Import only first 100 rows
python reset_and_import.py testing2.csv 100
```

## Manual Steps (if needed)

If you prefer to do it manually:

```bash
# 1. Delete database
rm riskchain.db

# 2. Initialize fresh database
python -c "from database import init_db; init_db()"

# 3. Import CSV
python import_csv_data.py testing2.csv
```

## Column Validation

The import script automatically:
- ✅ Checks for expected columns
- ✅ Warns about missing columns
- ✅ Shows extra columns found
- ✅ Displays column count and names

## Default CSV

The default CSV file is now `testing2.csv` (changed from `car_insurance_training_dataset_with_images.csv`).

