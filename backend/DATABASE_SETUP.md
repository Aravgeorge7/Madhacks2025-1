# Database Setup Instructions

## Quick Start

The database file (`riskchain.db`) is **not** included in the repository (it's in `.gitignore`). 
Your teammates need to recreate it using the CSV import script.

## Steps to Set Up Database

1. **Activate virtual environment:**
   ```bash
   cd /path/to/Madhacks2025-1
   source venv/bin/activate
   ```

2. **Initialize the database:**
   ```bash
   cd backend
   python -c "from database import init_db; init_db()"
   ```

3. **Import CSV data:**
   ```bash
   python import_csv_data.py ../car_insurance_training_dataset_with_images.csv
   ```

This will:
- Create the database schema
- Import all 350 claims from the CSV
- Calculate risk scores for each claim
- Set up the graph connections

## Database Location

After setup, the database will be created at:
- `backend/riskchain.db`

## What Gets Imported

- **350 claims** from the CSV file
- All claim fields (policy number, dates, vehicle info, etc.)
- Risk scores calculated via graph analysis
- Graph connections (doctors, lawyers, IP addresses)

## Notes

- The database is automatically created on first run
- Images are NOT downloaded (they were removed per requirements)
- All claims will have status "pending" or "unsettled" by default
- Risk scores are calculated automatically during import

