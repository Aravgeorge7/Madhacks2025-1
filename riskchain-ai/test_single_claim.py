"""
Quick manual scorer for a single claim.

Usage:
  python test_single_claim.py                # uses SAMPLE_CLAIM below
  python test_single_claim.py --claim-json path/to/claim.json

Requires a trained model (run model_training.py first).
"""

import argparse
import json
from pathlib import Path

from graph_engine.graph_engine import build_graph
from risk_model import predict_risk


# Update this template or provide a JSON file via --claim-json
SAMPLE_CLAIM = {
    "claim_id": "TEST123",
    "claim_submission_date": "2025-01-10",
    "accident_date": "2025-01-05",
    "accident_time": "14:30:00",
    "accident_location_city": "Springfield",
    "accident_location_state": "CA",
    "accident_description": "Rear-ended at a stop light.",
    "police_report_filed": 1,
    "loss_type": "collision",
    "claimant_age": 34,
    "claimant_gender": "male",
    "claimant_city": "Springfield",
    "claimant_state": "CA",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_year": 2018,
    "vehicle_use_type": "personal",
    "vehicle_mileage": 55000,
    "damage_severity": "moderate",
    "injury_severity": "minor",
    "medical_treatment_received": 1,
    "medical_cost_estimate": 5200,
    "airbags_deployed": 1,
    "policy_tenure_months": 40,
    "coverage_type": "collision",
    "policy_type": "collision_only",
    "deductible_amount": 500,
    "previous_claims_count": 0,
    "lawyer_name": "Smith & Assoc",
    "medical_provider_name": "Dr. Garcia",
    "repair_shop_name": "Premium Auto",
    "reported_by": "self",
    "fraud_label": 0,
    "claim_amount": 7000,
    "ip_address": "10.0.0.5",
    "phone_number": "+1-555-111-2222",
    "email": "user@example.com",
    "address": "123 Main St",
    "device_id": "DEV-1234",
}


def load_claim(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Score a single claim with the trained model.")
    parser.add_argument("--claim-json", type=str, default=None, help="Path to claim JSON file.")
    args = parser.parse_args()

    if args.claim_json:
        claim_path = Path(args.claim_json)
        if not claim_path.exists():
            raise FileNotFoundError(f"Claim JSON not found: {claim_path}")
        claim = load_claim(claim_path)
    else:
        claim = SAMPLE_CLAIM

    # Build a tiny graph for graph features
    engine = build_graph([claim])

    score = predict_risk(claim, graph_engine=engine)
    print(f"Risk score for claim {claim.get('claim_id', 'N/A')}: {score:.2f} (0-100 scale)")


if __name__ == "__main__":
    main()
