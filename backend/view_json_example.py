"""
Example script to view how JSON data is stored in the database
"""

from database import SessionLocal, Claim
import json

def view_claim_json(claim_id: str = None):
    """
    View the JSON structure of a claim in the database.
    
    Usage:
        view_claim_json("C12345678")  # View specific claim
        view_claim_json()  # View all claims
    """
    db = SessionLocal()
    
    try:
        if claim_id:
            claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
            if not claim:
                print(f"Claim {claim_id} not found")
                return
            
            print("=" * 80)
            print(f"CLAIM ID: {claim.claim_id}")
            print("=" * 80)
            print("\n📋 STRUCTURED FIELDS (Individual Columns):")
            print(f"  Claimant Name: {claim.claimant_name}")
            print(f"  Doctor: {claim.doctor}")
            print(f"  Lawyer: {claim.lawyer}")
            print(f"  IP Address: {claim.ip_address}")
            print(f"  Accident Type: {claim.accident_type}")
            print(f"  Risk Score: {claim.risk_score}/100 ({claim.risk_category})")
            
            print("\n📦 COMPLETE JSON DATA (claim_data_json field):")
            print(json.dumps(claim.claim_data_json, indent=2, default=str))
            
            print("\n📄 MISSING DOCS (JSON array):")
            print(json.dumps(claim.missing_docs, indent=2))
            
        else:
            # View all claims
            claims = db.query(Claim).all()
            print(f"\nTotal Claims in Database: {len(claims)}\n")
            
            for claim in claims:
                print("=" * 80)
                print(f"Claim ID: {claim.claim_id}")
                print(f"Claimant: {claim.claimant_name}")
                print(f"Risk Score: {claim.risk_score}/100")
                print("\nComplete JSON:")
                print(json.dumps(claim.claim_data_json, indent=2, default=str))
                print("\n")
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        view_claim_json(sys.argv[1])
    else:
        view_claim_json()

