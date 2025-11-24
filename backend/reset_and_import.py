#!/usr/bin/env python3
"""
Reset database and import data from testing2.csv in one command.

Usage:
    python reset_and_import.py [csv_file] [limit]
    
Examples:
    python reset_and_import.py                    # Uses testing2.csv, no limit
    python reset_and_import.py testing2.csv      # Specify CSV file
    python reset_and_import.py testing2.csv 100  # Import only first 100 rows
"""

import os
import sys
from pathlib import Path
from database import init_db
from import_csv_data import import_csv_data

def reset_database():
    """Delete the database file to start fresh."""
    db_path = Path("riskchain.db")
    
    if db_path.exists():
        print("🗑️  Deleting existing database...")
        os.remove(db_path)
        print("✅ Database deleted successfully")
    else:
        print("ℹ️  No existing database found (this is fine for first run)")
    
    # Also delete any database backup files
    for backup in Path(".").glob("riskchain.db.*"):
        if backup.is_file():
            print(f"🗑️  Deleting backup: {backup}")
            backup.unlink()


def main():
    """Main function: reset database and import CSV."""
    print("=" * 80)
    print("Database Reset and Import")
    print("=" * 80)
    print()
    
    # Step 1: Reset database
    reset_database()
    print()
    
    # Step 2: Initialize fresh database
    print("🔧 Initializing fresh database...")
    init_db()
    print("✅ Database initialized")
    print()
    
    # Step 3: Import CSV data
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "testing2.csv"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not Path(csv_file).exists():
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Looking for: {Path(csv_file).absolute()}")
        sys.exit(1)
    
    print(f"📥 Importing data from: {csv_file}")
    if limit:
        print(f"   Limit: {limit} rows")
    print()
    
    import_csv_data(csv_file, limit=limit)
    
    print()
    print("=" * 80)
    print("✅ Database reset and import complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

