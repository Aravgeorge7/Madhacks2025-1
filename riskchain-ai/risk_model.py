import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # dependency may be unavailable offline
    SentenceTransformer = None
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from graph_engine.graph_features import GraphFeatures
from graph_engine.graph_engine import GraphEngine


@dataclass
class RiskModelArtifacts:
    model_path: str
    feature_columns_path: str
    graph_metadata_path: str


class RiskModel:
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(artifacts_dir, exist_ok=True)
        self.model: Optional[XGBClassifier] = None
        self.feature_columns: Optional[List[str]] = None
        self.text_vectorizer: Optional[TfidfVectorizer] = None
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            self.text_encoder_type = "transformer"
        except Exception:
            self.embedder = None
            self.text_encoder_type = "tfidf"

    # ------------------------------------------------------------------ #
    # Feature engineering
    # ------------------------------------------------------------------ #
    def _prepare_base_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
        df = df.copy()
        df["accident_date"] = pd.to_datetime(df["accident_date"], errors="coerce")
        df["claim_submission_date"] = pd.to_datetime(df["claim_submission_date"], errors="coerce")
        df["days_between_accident_and_claim"] = (df["claim_submission_date"] - df["accident_date"]).dt.days.fillna(0)
        df["vehicle_year"] = pd.to_numeric(df.get("vehicle_year", 0), errors="coerce").fillna(0)
        df["car_age"] = 2025 - df["vehicle_year"]

        # photos column may be missing or scalar; normalize to a Series
        if "photos" in df.columns:
            photos = pd.to_numeric(df["photos"], errors="coerce").fillna(1)
        else:
            photos = pd.Series(1, index=df.index)
        df["missing_docs"] = 1 - photos

        numeric_cols = [
            "claim_amount",
            "medical_cost_estimate",
            "deductible_amount",
            "previous_claims_count",
            "policy_tenure_months",
            "vehicle_mileage",
            "claimant_age",
            "days_between_accident_and_claim",
            "car_age",
        ]

        categorical_cols = [
            "loss_type",
            "claimant_gender",
            "claimant_state",
            "accident_location_state",
            "vehicle_make",
            "vehicle_model",
            "vehicle_use_type",
            "damage_severity",
            "injury_severity",
            "coverage_type",
            "policy_type",
            "lawyer_name",
            "medical_provider_name",
        ]

        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
        # Columns that commonly have NaN in training data (from CSV's "None" values)
        nan_allowed_cols = {"lawyer_name", "medical_provider_name"}

        for col in categorical_cols:
            if col not in df.columns:
                # Only use NaN for columns that had NaN during training
                df[col] = np.nan if col in nan_allowed_cols else "unknown"
            else:
                if col in nan_allowed_cols:
                    # Replace "unknown", "None", empty strings with NaN for consistency with training
                    df[col] = df[col].replace({"unknown": np.nan, "None": np.nan, "": np.nan, "nan": np.nan})

        return df, numeric_cols, categorical_cols

    def _encode_text(self, descriptions: List[str], fit: bool) -> pd.DataFrame:
        # If we need transformer embeddings (either fitting with embedder or model expects them)
        if self.embedder is not None:
            embeddings = self.embedder.encode(descriptions)
            return pd.DataFrame(embeddings, columns=[f"text_emb_{i}" for i in range(embeddings.shape[1])])

        # If model was trained with transformer but embedder is not available,
        # output zeros with correct column names for alignment
        if self.text_encoder_type == "transformer" and not fit:
            # all-MiniLM-L6-v2 produces 384-dimensional embeddings
            n_dims = 384
            zeros = np.zeros((len(descriptions), n_dims))
            print(f"WARNING: Using zero embeddings for {len(descriptions)} descriptions (transformer unavailable)")
            return pd.DataFrame(zeros, columns=[f"text_emb_{i}" for i in range(n_dims)])

        # Fall back to TF-IDF for training without transformer or if explicitly using tfidf
        if self.text_vectorizer is None:
            self.text_vectorizer = TfidfVectorizer(max_features=256, ngram_range=(1, 2))

        if fit or not hasattr(self.text_vectorizer, "vocabulary_"):
            matrix = self.text_vectorizer.fit_transform(descriptions)
        else:
            matrix = self.text_vectorizer.transform(descriptions)

        return pd.DataFrame(matrix.toarray(), columns=[f"tfidf_{i}" for i in range(matrix.shape[1])])

    def _build_design_matrix(
        self,
        df: pd.DataFrame,
        graph_engine: Optional[GraphEngine] = None,
        include_graph: bool = True,
        include_gnn: bool = False,
        fit: bool = True,
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        df, numeric_cols, categorical_cols = self._prepare_base_features(df)
        claim_ids = df["claim_id"].astype(str)

        # Text embeddings
        text_df = self._encode_text(
            df.get("accident_description", "").fillna("").tolist(), fit=fit
        )
        text_df.index = claim_ids

        # Graph features
        graph_df = pd.DataFrame()
        if include_graph and graph_engine is not None:
            gf = GraphFeatures(graph_engine)
            graph_df = gf.compute_features_for_claims(df.to_dict("records"))
            graph_df.index = claim_ids

        X_tabular = df[numeric_cols + categorical_cols]
        y = df["fraud_label"].astype(int) if "fraud_label" in df.columns else None

        if fit or not hasattr(self, "preprocessor"):
            numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
            # Handle both new (sparse_output) and old (sparse) sklearn
            try:
                ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            except TypeError:
                ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
            categorical_transformer = Pipeline(steps=[("encoder", ohe)])
            self.preprocessor = ColumnTransformer(
                transformers=[
                    ("num", numeric_transformer, numeric_cols),
                    ("cat", categorical_transformer, categorical_cols),
                ],
                remainder="drop",
            )
            tabular_array = self.preprocessor.fit_transform(X_tabular)
        else:
            tabular_array = self.preprocessor.transform(X_tabular)

        tabular_df = pd.DataFrame(
            tabular_array,
            index=claim_ids,
            columns=self._column_names(self.preprocessor),
        )

        # Optional GNN embeddings
        gnn_df = pd.DataFrame()
        if include_gnn and graph_engine is not None:
            gnn_df = graph_engine.compute_gnn_embeddings(tabular_df)
            gnn_df = gnn_df.set_index("claim_id").reindex(claim_ids).fillna(0.0)

        # Assemble final frame
        pieces = [tabular_df, text_df]
        if not graph_df.empty:
            pieces.append(graph_df)
        if not gnn_df.empty:
            pieces.append(gnn_df)

        final_df = pd.concat(pieces, axis=1)
        final_df.index = claim_ids
        if fit:
            self.feature_columns = final_df.columns.tolist()
        else:
            missing = [c for c in self.feature_columns if c not in final_df.columns]
            for c in missing:
                final_df[c] = 0.0
            final_df = final_df[self.feature_columns]
        return final_df, y

    # ------------------------------------------------------------------ #
    # Training and prediction
    # ------------------------------------------------------------------ #
    def train(
        self,
        df: pd.DataFrame,
        graph_engine: Optional[GraphEngine] = None,
        include_graph: bool = True,
        include_gnn: bool = False,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, float]:
        X, y = self._build_design_matrix(df, graph_engine, include_graph, include_gnn)

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            scale_pos_weight=float((y == 0).sum()) / max((y == 1).sum(), 1),
        )
        self.model.fit(X_train, y_train)

        val_probs = self.model.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)

        metrics = {
            "precision": precision_score(y_val, val_preds, zero_division=0),
            "recall": recall_score(y_val, val_preds, zero_division=0),
            "f1": f1_score(y_val, val_preds, zero_division=0),
            "auc": roc_auc_score(y_val, val_probs),
        }

        return metrics

    def predict_proba(
        self,
        claims: List[dict],
        graph_engine: Optional[GraphEngine] = None,
        include_graph: bool = True,
        include_gnn: bool = False,
    ) -> List[float]:
        if self.model is None:
            self.load()
        df = pd.DataFrame(claims)
        X, _ = self._build_design_matrix(df, graph_engine, include_graph, include_gnn, fit=False)
        probs = self.model.predict_proba(X)[:, 1]
        return probs.tolist()

    def predict_risk_scores(
        self,
        claims: List[dict],
        graph_engine: Optional[GraphEngine] = None,
    ) -> List[float]:
        probs = self.predict_proba(claims, graph_engine)
        gf = GraphFeatures(graph_engine) if graph_engine else None
        results = []
        for claim, p in zip(claims, probs):
            graph_risk = gf.compute_graph_risk(claim) / 30.0 if gf else 0
            rule_adj = self._rule_adjustment(claim)
            final_score = min(100.0, (p * 70) + (graph_risk * 20 * 1.0) + rule_adj)
            results.append(final_score)
        return results

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save(self) -> RiskModelArtifacts:
        model_path = os.path.join(self.artifacts_dir, "risk_model.pkl")
        feature_path = os.path.join(self.artifacts_dir, "feature_columns.json")
        joblib.dump(
            {
                "model": self.model,
                "preprocessor": self.preprocessor,
                "text_vectorizer": self.text_vectorizer,
                "text_encoder_type": self.text_encoder_type,
            },
            model_path,
        )
        with open(feature_path, "w", encoding="utf-8") as f:
            json.dump(
                {"columns": self.feature_columns, "text_encoder_type": self.text_encoder_type}, f
            )
        return RiskModelArtifacts(
            model_path=model_path,
            feature_columns_path=feature_path,
            graph_metadata_path=os.path.join(self.artifacts_dir, "graph_metadata.json"),
        )

    def load(self):
        model_path = os.path.join(self.artifacts_dir, "risk_model.pkl")
        feature_path = os.path.join(self.artifacts_dir, "feature_columns.json")
        data = joblib.load(model_path)
        self.model = data["model"]
        self.preprocessor = data["preprocessor"]
        self.text_vectorizer = data.get("text_vectorizer")
        saved_encoder_type = data.get("text_encoder_type", "transformer")
        with open(feature_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self.feature_columns = meta["columns"]
            saved_encoder_type = meta.get("text_encoder_type", saved_encoder_type)

        # Validate text encoder compatibility
        if saved_encoder_type == "transformer" and self.embedder is None:
            print("WARNING: Model was trained with transformer embeddings but SentenceTransformer is not available!")
            print("Attempting to load SentenceTransformer...")
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
                self.text_encoder_type = "transformer"
                print("✅ Successfully loaded SentenceTransformer")
            except Exception as e:
                print(f"❌ Failed to load SentenceTransformer: {e}")
                print("Predictions may be inaccurate due to text encoder mismatch!")
                self.text_encoder_type = saved_encoder_type  # Keep the saved type for feature alignment
        else:
            self.text_encoder_type = saved_encoder_type

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _column_names(self, preprocessor: ColumnTransformer) -> List[str]:
        output_features = []
        for name, trans, cols in preprocessor.transformers_:
            if name == "remainder":
                continue
            if hasattr(trans, "get_feature_names_out"):
                feature_names = list(trans.get_feature_names_out(cols))
            else:
                feature_names = cols
            output_features.extend(feature_names)
        return output_features

    def _rule_adjustment(self, claim: dict) -> float:
        adj = 0.0
        if claim.get("police_report_filed") == 0:
            adj += 5
        if claim.get("previous_claims_count", 0) >= 3:
            adj += 5
        if claim.get("medical_provider_name") and claim.get("lawyer_name"):
            adj += 3
        return adj


def predict_risk(claim: dict, graph_engine: Optional[GraphEngine] = None) -> float:
    """
    Convenience API for single-claim scoring using saved artifacts.
    """
    model = RiskModel()
    model.load()
    return model.predict_risk_scores([claim], graph_engine=graph_engine)[0]
