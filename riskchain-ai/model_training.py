import os
from pathlib import Path
from typing import Dict

import pandas as pd
from sklearn.model_selection import train_test_split

from graph_engine.graph_engine import GraphEngine
from risk_model import RiskModel
from synthetic_data import load_real_claims


class ClaimDataset:
    """Lightweight dataset wrapper to manage splits used by training."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def train_val_test_split(self, test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42):
        train_df, temp_df = train_test_split(self.df, test_size=test_size + val_size, random_state=random_state, stratify=self.df["fraud_label"])
        relative_val_size = val_size / (test_size + val_size)
        val_df, test_df = train_test_split(temp_df, test_size=relative_val_size, random_state=random_state, stratify=temp_df["fraud_label"])
        return train_df, val_df, test_df


def train_model(
    real_data_path: str = "../car_insurance_training_dataset_with_images.csv",
    artifacts_dir: str = "artifacts",
    augment_with_synthetic: bool = True,
) -> Dict[str, float]:
    """
    End-to-end training: load real data and optionally augment with synthetic fraud,
    build graph, train model, return validation metrics.
    """
    base_dir = Path(__file__).resolve().parent
    data_path = Path(real_data_path)
    if not data_path.is_absolute():
        data_path = base_dir / data_path

    from synthetic_data import generate_synthetic_claims

    real_df = load_real_claims(str(data_path))

    # If real data has no fraud, augment with synthetic fraud examples
    if augment_with_synthetic and real_df["fraud_label"].sum() == 0:
        print("Real data has no fraud examples, augmenting with synthetic data...")
        # Generate synthetic fraud and non-fraud claims
        synthetic_df = generate_synthetic_claims(normal=100, suspicious=80, organized_rings=5)
        # Combine real (non-fraud) with synthetic
        real_df = pd.concat([real_df, synthetic_df], ignore_index=True)
        print(f"Combined dataset: {len(real_df)} claims, {real_df['fraud_label'].sum()} fraud")

    # Shuffle for randomness
    df = real_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Build graph from combined claims
    graph_engine = GraphEngine()
    graph_engine.build_graph(df.to_dict("records"))

    artifacts_path = Path(artifacts_dir)
    if not artifacts_path.is_absolute():
        artifacts_path = base_dir / artifacts_path

    model = RiskModel(artifacts_dir=str(artifacts_path))
    metrics = model.train(df, graph_engine=graph_engine, include_graph=True, include_gnn=False)
    model.save()

    return metrics


if __name__ == "__main__":
    metrics = train_model()
    print("Validation metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
