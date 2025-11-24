"""
Import CSV data into database and download images
"""

import csv
import os
import requests
from datetime import datetime
from pathlib import Path
from database import SessionLocal, Claim, init_db
from graph_service import RiskGraph
import uuid

# Create images directory
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Initialize graph service
risk_graph = RiskGraph()


def download_image(url: str, claim_id: str) -> str:
    """
    Download image from URL and save locally.
    
    Returns:
        Local file path if successful, None otherwise
    """
    if not url or url == "None" or url.strip() == "":
        return None
    
    try:
        # Get file extension from URL or default to jpg
        ext = url.split('.')[-1].split('?')[0] if '.' in url else 'jpg'
        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
            ext = 'jpg'
        
        filename = f"{claim_id}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = IMAGES_DIR / filename
        
        # Download image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save to disk
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return str(filepath)
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    if not date_str or date_str == "None":
        return None
    
    try:
        # Try different date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return None
    except:
        return None


def parse_time(time_str: str) -> str:
    """Parse time string."""
    if not time_str or time_str == "None":
        return None
    return time_str.strip()


def parse_int(value: str) -> int:
    """Parse integer value."""
    if not value or value == "None" or value.strip() == "":
        return 0
    try:
        return int(float(value))
    except:
        return 0


def parse_float(value: str) -> float:
    """Parse float value."""
    if not value or value == "None" or value.strip() == "":
        return None
    try:
        return float(value)
    except:
        return None


def import_csv_data(csv_file_path: str, limit: int = None):
    """
    Import CSV data into database.
    
    Args:
        csv_file_path: Path to CSV file
        limit: Optional limit on number of records to import
    """
    db = SessionLocal()
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_columns = reader.fieldnames
            
            # Expected columns (for validation)
            expected_columns = [
                'claim_id', 'policy_number', 'claim_submission_date', 'accident_date',
                'accident_time', 'accident_location_city', 'accident_location_state',
                'accident_description', 'police_report_filed', 'loss_type',
                'claimant_age', 'claimant_gender', 'claimant_city', 'claimant_state',
                'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_use_type',
                'vehicle_mileage', 'damage_severity', 'injury_severity',
                'medical_treatment_received', 'medical_cost_estimate', 'airbags_deployed',
                'policy_tenure_months', 'coverage_type', 'policy_type', 'deductible_amount',
                'previous_claims_count', 'lawyer_name', 'medical_provider_name',
                'repair_shop_name', 'reported_by', 'status', 'fraud_label', 'photos'
            ]
            
            # Check for missing columns
            missing_columns = [col for col in expected_columns if col not in csv_columns]
            extra_columns = [col for col in csv_columns if col not in expected_columns]
            
            print(f"Starting import from {csv_file_path}...")
            print("=" * 80)
            print(f"CSV Columns Found: {len(csv_columns)}")
            print(f"  Columns: {', '.join(csv_columns[:10])}{'...' if len(csv_columns) > 10 else ''}")
            
            if missing_columns:
                print(f"⚠️  Warning: Missing expected columns: {missing_columns}")
            if extra_columns:
                print(f"ℹ️  Info: Extra columns found: {extra_columns}")
            print("=" * 80)
            
            total_rows = 0
            imported = 0
            errors = 0
            
            for row_num, row in enumerate(reader, 1):
                if limit and row_num > limit:
                    break
                
                total_rows += 1
                
                try:
                    claim_id = row.get('claim_id', '').strip()
                    if not claim_id:
                        claim_id = f"C{str(uuid.uuid4())[:8].upper()}"
                    
                    # Check if claim already exists
                    existing = db.query(Claim).filter(Claim.claim_id == claim_id).first()
                    if existing:
                        print(f"⏭️  Skipping {claim_id} - already exists")
                        continue
                    
                    # Download image
                    photo_url = row.get('photos', '').strip()
                    photo_path = None
                    if photo_url and photo_url != "None":
                        photo_path = download_image(photo_url, claim_id)
                        if photo_path:
                            print(f"📥 Downloaded image for {claim_id}")
                    
                    # Parse dates
                    claim_submission_date = parse_date(row.get('claim_submission_date'))
                    accident_date = parse_date(row.get('accident_date'))
                    accident_time = parse_time(row.get('accident_time'))
                    
                    # Create claim data for graph processing
                    graph_claim_data = {
                        "claim_id": claim_id,
                        "claimant_name": f"{row.get('claimant_city', 'Unknown')} Claimant",
                        "doctor": row.get('medical_provider_name', '') or 'None',
                        "lawyer": row.get('lawyer_name', '') or 'None',
                        "ip_address": f"192.168.1.{row_num % 255}",  # Mock IP for CSV data
                        "missing_docs": [] if parse_int(row.get('police_report_filed')) else ['police_report'],
                        "fraud_nlp_score": 0
                    }
                    
                    # Process through graph service
                    graph_result = risk_graph.process_claim(graph_claim_data)
                    
                    # Create complete JSON data
                    claim_json = dict(row)
                    claim_json['photo_local_path'] = photo_path
                    
                    # Create database record
                    db_claim = Claim(
                        claim_id=claim_id,
                        policy_number=row.get('policy_number', '').strip() or None,
                        claim_submission_date=claim_submission_date,
                        accident_date=accident_date,
                        accident_time=accident_time,
                        accident_location_city=row.get('accident_location_city', '').strip() or None,
                        accident_location_state=row.get('accident_location_state', '').strip() or None,
                        accident_description=row.get('accident_description', '').strip() or None,
                        police_report_filed=parse_int(row.get('police_report_filed')),
                        loss_type=row.get('loss_type', '').strip() or None,
                        claimant_age=parse_int(row.get('claimant_age')),
                        claimant_gender=row.get('claimant_gender', '').strip() or None,
                        claimant_city=row.get('claimant_city', '').strip() or None,
                        claimant_state=row.get('claimant_state', '').strip() or None,
                        vehicle_make=row.get('vehicle_make', '').strip() or None,
                        vehicle_model=row.get('vehicle_model', '').strip() or None,
                        vehicle_year=parse_int(row.get('vehicle_year')),
                        vehicle_use_type=row.get('vehicle_use_type', '').strip() or None,
                        vehicle_mileage=parse_int(row.get('vehicle_mileage')),
                        damage_severity=row.get('damage_severity', '').strip() or None,
                        injury_severity=row.get('injury_severity', '').strip() or None,
                        medical_treatment_received=parse_int(row.get('medical_treatment_received')),
                        medical_cost_estimate=parse_float(row.get('medical_cost_estimate')),
                        airbags_deployed=parse_int(row.get('airbags_deployed')),
                        policy_tenure_months=parse_int(row.get('policy_tenure_months')),
                        coverage_type=row.get('coverage_type', '').strip() or None,
                        policy_type=row.get('policy_type', '').strip() or None,
                        deductible_amount=parse_float(row.get('deductible_amount')),
                        previous_claims_count=parse_int(row.get('previous_claims_count')),
                        lawyer_name=row.get('lawyer_name', '').strip() or None,
                        medical_provider_name=row.get('medical_provider_name', '').strip() or None,
                        repair_shop_name=row.get('repair_shop_name', '').strip() or None,
                        reported_by=row.get('reported_by', '').strip() or None,
                        photos_url=photo_url or None,
                        photos_local_path=photo_path,
                        fraud_label=parse_int(row.get('fraud_label')),
                        status=row.get('status', 'pending').strip() or 'pending',
                        
                        # Risk scoring
                        risk_score=graph_result["risk_score"],
                        risk_category=graph_result["risk_category"],
                        fraud_nlp_score=graph_result.get("fraud_nlp_score", 0),
                        
                        # JSON storage
                        claim_data_json=claim_json,
                        
                        # Legacy fields (mapped from CSV)
                        claimant_name=f"{row.get('claimant_city', 'Unknown')} Claimant",
                        doctor=row.get('medical_provider_name', '') or None,
                        lawyer=row.get('lawyer_name', '') or None,
                        ip_address=f"192.168.1.{row_num % 255}",
                        accident_type=row.get('loss_type', ''),
                        claim_date=accident_date or claim_submission_date or datetime.utcnow(),
                    )
                    
                    db.add(db_claim)
                    imported += 1
                    
                    if imported % 100 == 0:
                        db.commit()
                        print(f"✅ Imported {imported} claims...")
                
                except Exception as e:
                    errors += 1
                    print(f"❌ Error importing row {row_num}: {e}")
                    continue
            
            # Final commit
            db.commit()
            
            print("=" * 80)
            print(f"✅ Import complete!")
            print(f"   Total rows processed: {total_rows}")
            print(f"   Successfully imported: {imported}")
            print(f"   Errors: {errors}")
            print(f"   Images downloaded to: {IMAGES_DIR.absolute()}")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "testing2.csv"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Initialize database
    init_db()
    
    # Import data
    import_csv_data(csv_file, limit=limit)

