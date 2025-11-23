import random
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_synthetic_claims(
    normal: int = 120,
    suspicious: int = 60,
    organized_rings: int = 3,
) -> pd.DataFrame:
    """
    Create synthetic claims including normal noise, lightly suspicious cases,
    and organized rings with shared providers/lawyers/IPs.
    """
    rows = []
    base_start = datetime(2023, 1, 1)
    base_end = datetime(2025, 12, 31)

    # --- Normal claims ---
    for i in range(normal):
        rows.append(_random_claim(base_start, base_end, fraud_label=0))

    # --- Slightly suspicious ---
    for i in range(suspicious):
        rows.append(_random_claim(base_start, base_end, fraud_label=1, mild=True))

    # --- Organized rings ---
    for r in range(organized_rings):
        doctor = f"RingDoctor_{r}"
        lawyer = f"RingLaw_{r}"
        ip = f"192.168.{r}.100"
        address = f"{100 + r} Elm St"
        for j in range(6):
            rows.append(
                _random_claim(
                    base_start,
                    base_end,
                    fraud_label=1,
                    ring_entities={"medical_provider_name": doctor, "lawyer_name": lawyer, "ip_address": ip, "address": address},
                    amount=14000 + random.randint(-800, 800),
                )
            )

    return pd.DataFrame(rows)


def _random_claim(start: datetime, end: datetime, fraud_label: int, mild: bool = False, ring_entities=None, amount: int = None):
    accident_date = _random_date(start, end)
    submission_date = accident_date + timedelta(days=random.randint(0, 14 if fraud_label else 30))
    vehicle_year = random.randint(2005, 2023)
    device_id = f"DEV-{random.randint(1000,9999)}"
    ring_entities = ring_entities or {}

    loss_type = random.choice(["collision", "comprehensive", "theft"])
    injury_severity = random.choice(["none", "minor", "moderate", "severe"])
    damage_severity = random.choice(["minor", "moderate", "major", "total_loss"])

    base_amount = amount if amount is not None else random.randint(3000, 18000)
    if mild:
        base_amount += random.randint(2000, 6000)

    claim_id = f"CLM_SYN_{random.randint(100000, 999999)}"
    policy_number = f"POL_SYN_{random.randint(100000, 999999)}"

    return {
        "claim_id": claim_id,
        "policy_number": policy_number,
        "claim_submission_date": submission_date.strftime("%Y-%m-%d"),
        "accident_date": accident_date.strftime("%Y-%m-%d"),
        "accident_time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:00",
        "accident_location_city": random.choice(["Springfield", "Fairview", "Riverside", "Hill Valley"]),
        "accident_location_state": random.choice(["CA", "NY", "TX", "FL", "IL"]),
        "accident_description": random.choice(
            [
                "Rear-ended at a stop light.",
                "Single car skid on wet road.",
                "Minor fender bender in parking lot.",
                "Whiplash after being cut off in traffic.",
            ]
        ),
        "police_report_filed": int(random.random() > 0.2),
        "loss_type": loss_type,
        "claimant_age": random.randint(18, 80),
        "claimant_gender": random.choice(["male", "female"]),
        "claimant_city": random.choice(["Springfield", "Fairview", "Riverside", "Hill Valley"]),
        "claimant_state": random.choice(["CA", "NY", "TX", "FL", "IL"]),
        "vehicle_make": random.choice(["Toyota", "Honda", "Ford", "Chevrolet"]),
        "vehicle_model": random.choice(["Camry", "Accord", "F-150", "Civic"]),
        "vehicle_year": vehicle_year,
        "vehicle_use_type": random.choice(["personal", "commercial"]),
        "vehicle_mileage": random.randint(10000, 180000),
        "damage_severity": damage_severity,
        "injury_severity": injury_severity,
        "medical_treatment_received": int(random.random() > 0.3),
        "medical_cost_estimate": base_amount * random.uniform(0.3, 0.8),
        "airbags_deployed": int(random.random() > 0.4),
        "policy_tenure_months": random.randint(1, 120),
        "coverage_type": random.choice(["collision", "comprehensive", "liability"]),
        "policy_type": random.choice(["collision_only", "full", "liability_only"]),
        "deductible_amount": random.choice([250, 500, 750, 1000]),
        "previous_claims_count": random.randint(0, 4 if fraud_label else 2),
        "lawyer_name": ring_entities.get("lawyer_name") if ring_entities else random.choice(["Smith & Assoc", "Davis Law", "None"]),
        "medical_provider_name": ring_entities.get("medical_provider_name") if ring_entities else random.choice(["WellCare Clinic", "Dr. Garcia", "Chiro Plus"]),
        "repair_shop_name": ring_entities.get("repair_shop_name") if ring_entities else random.choice(["Premium Auto", "AutoFix", "SpeedyRepair"]),
        "reported_by": random.choice(["self", "agent", "police"]),
        "fraud_label": fraud_label,
        "status": "open",
        "claim_amount": base_amount,
        "ip_address": ring_entities.get("ip_address") if ring_entities else f"10.0.{random.randint(0,20)}.{random.randint(1,200)}",
        "device_id": ring_entities.get("device_id", device_id),
        "email": f"user{random.randint(1000,9999)}@example.com",
        "phone_number": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "address": ring_entities.get("address", f"{random.randint(10,999)} Oak Ave"),
    }


def load_real_claims(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Ensure expected columns exist
    if "claim_amount" not in df.columns:
        df["claim_amount"] = df.get("medical_cost_estimate", 0) + df.get("deductible_amount", 0)
    if "fraud_label" not in df.columns:
        df["fraud_label"] = 0
    return df
