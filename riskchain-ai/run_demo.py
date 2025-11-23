"""
End-to-end demonstration (real data only):
1. Load provided claims.
2. Build graph.
3. Train ML risk model.
4. Score claims and print top risks.
5. Detect fraud rings.
"""

import json
import os

from pathlib import Path
import pandas as pd

from fraud_ring_detection import detect_fraud_rings
from graph_engine.graph_engine import GraphEngine
from risk_model import RiskModel
from synthetic_data import load_real_claims


def run():
    base_dir = Path(__file__).resolve().parent
    real_path = base_dir / "car_insurance_dataset_augmented.csv"
    print("Loading provided dataset...")
    real_df = load_real_claims(str(real_path))

    df = real_df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"Total training rows: {len(df)} (real only)")

    graph_engine = GraphEngine()
    graph_engine.build_graph(df.to_dict("records"))
    print("Graph summary:", graph_engine.summary())

    model = RiskModel(artifacts_dir=str(base_dir / "artifacts"))
    metrics = model.train(df, graph_engine=graph_engine, include_graph=True, include_gnn=False)
    model.save()
    print("Validation metrics:", json.dumps(metrics, indent=2))

    # Score a handful of claims (latest rows)
    sample_claims = df.tail(5).to_dict("records")
    scores = model.predict_risk_scores(sample_claims, graph_engine=graph_engine)
    for claim, score in zip(sample_claims, scores):
        print(f"Claim {claim['claim_id']} risk → {score:.2f}")

    # Fraud ring detection
    ring_report = detect_fraud_rings(graph_engine)
    print(f"Detected {len(ring_report['fraud_rings'])} fraud ring(s)")
    for ring in ring_report["fraud_rings"]:
        print(f"- Ring score {ring['score']} with {ring['claim_count']} claims; provider={ring['dominant_provider']} lawyer={ring['dominant_lawyer']}")

    report_dir = base_dir / "artifacts"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "graph_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(ring_report, f, indent=2)
    print(f"Graph + ring report saved to {report_path}")


if __name__ == "__main__":
    run()
