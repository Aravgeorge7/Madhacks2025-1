import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

import networkx as nx
import pandas as pd

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:  # torch is optional; we degrade gracefully
    torch = None


class GraphEngine:
    """
    Builds an entity graph for insurance fraud analysis.

    Nodes: claims + people + providers + lawyers + IP/phone/email/address/device.
    Edges: claim -> entity (typed), claim -> claim (similarity/time proximity).
    """

    def __init__(self):
        self.G = nx.Graph()
        self.claim_records: Dict[str, dict] = {}

    # ------------------------------------------------------------------ #
    # Graph construction
    # ------------------------------------------------------------------ #
    def add_claim(self, claim: dict):
        claim_id = str(
            claim.get("claim_id")
            or claim.get("policy_number")
            or f"claim_{len(self.claim_records) + 1}"
        )
        claim["claim_id"] = claim_id
        self.claim_records[claim_id] = claim

        self.G.add_node(claim_id, type="claim", **claim)

        entity_fields = {
            "claimant_name": "person",
            "lawyer_name": "lawyer",
            "medical_provider_name": "provider",
            "repair_shop_name": "shop",
            "ip_address": "ip",
            "phone_number": "phone",
            "email": "email",
            "address": "address",
            "device_id": "device",
            "vehicle_vin": "vehicle",
        }

        for key, node_type in entity_fields.items():
            val = claim.get(key)
            if val and str(val).strip():
                self.G.add_node(val, type=node_type)
                self.G.add_edge(claim_id, val, relation=node_type)

    def build_graph(self, claims: Sequence[dict]):
        for claim in claims:
            self.add_claim(claim)

        self._add_similarity_edges()
        self._add_time_proximity_edges()

    def _add_similarity_edges(self):
        """
        Connect claims that share key entities (doctor, lawyer, IP, address, etc.).
        These edges carry weights to be reused by scoring and the optional GNN.
        """
        keys = [
            "medical_provider_name",
            "lawyer_name",
            "ip_address",
            "address",
            "device_id",
            "email",
            "phone_number",
            "vehicle_vin",
        ]

        for key in keys:
            bucket: Dict[str, List[str]] = {}
            for cid, claim in self.claim_records.items():
                val = claim.get(key)
                if val and str(val).strip():
                    bucket.setdefault(val, []).append(cid)

            for val, claim_ids in bucket.items():
                if len(claim_ids) < 2:
                    continue
                for a, b in itertools.combinations(claim_ids, 2):
                    weight = 1.0
                    # heavier weight for coordinated professional edges
                    if key in {"medical_provider_name", "lawyer_name"}:
                        weight = 2.0
                    self.G.add_edge(a, b, relation=f"similar_{key}", weight=weight)

    def _add_time_proximity_edges(self, window_days: int = 7):
        """
        Adds edges between claims that occur close in time AND share geography/IP.
        """
        parsed: List[Tuple[str, datetime, dict]] = []
        for cid, claim in self.claim_records.items():
            date_val = claim.get("claim_submission_date") or claim.get("accident_date")
            if isinstance(date_val, str):
                try:
                    date_val = pd.to_datetime(date_val)
                except Exception:
                    date_val = None
            if not isinstance(date_val, pd.Timestamp):
                continue
            parsed.append((cid, date_val.to_pydatetime(), claim))

        parsed.sort(key=lambda x: x[1])
        for i, (cid, date_val, claim) in enumerate(parsed):
            for cid2, date_val2, claim2 in parsed[i + 1 :]:
                if (date_val2 - date_val) > timedelta(days=window_days):
                    break
                same_state = claim.get("accident_location_state") == claim2.get(
                    "accident_location_state"
                )
                shared_ip = claim.get("ip_address") and claim.get("ip_address") == claim2.get("ip_address")
                if same_state or shared_ip:
                    self.G.add_edge(
                        cid,
                        cid2,
                        relation="time_burst",
                        weight=1.5 if shared_ip else 0.8,
                        days_apart=(date_val2 - date_val).days,
                    )

    # ------------------------------------------------------------------ #
    # Optional: simple GNN to learn claim embeddings from the graph.
    # ------------------------------------------------------------------ #
    def compute_gnn_embeddings(
        self, claim_features: pd.DataFrame, hidden_dim: int = 32, out_dim: int = 16
    ) -> pd.DataFrame:
        if torch is None:
            # Torch not installed; return zeros so the pipeline can still run.
            zeros = pd.DataFrame(
                0.0, index=claim_features.index, columns=[f"gnn_emb_{i}" for i in range(out_dim)]
            )
            zeros.insert(0, "claim_id", claim_features.index)
            return zeros

        claim_ids = [cid for cid in self.G.nodes if self.G.nodes[cid].get("type") == "claim"]
        if not claim_ids:
            return pd.DataFrame(columns=["claim_id"] + [f"gnn_emb_{i}" for i in range(out_dim)])

        # Build claim-claim adjacency (projection)
        idx_map = {cid: idx for idx, cid in enumerate(claim_ids)}
        edges = []
        for a, b, data in self.G.edges(data=True):
            if a in idx_map and b in idx_map:
                edges.append((idx_map[a], idx_map[b], data.get("weight", 1.0)))

        if not edges:
            zeros = pd.DataFrame(
                0.0, index=claim_ids, columns=[f"gnn_emb_{i}" for i in range(out_dim)]
            )
            zeros.insert(0, "claim_id", claim_ids)
            return zeros

        edge_index = torch.tensor([[e[0] for e in edges], [e[1] for e in edges]], dtype=torch.long)
        weights = torch.tensor([e[2] for e in edges], dtype=torch.float32)

        # Build symmetric adjacency
        num_nodes = len(claim_ids)
        adj = torch.sparse_coo_tensor(edge_index, weights, (num_nodes, num_nodes))
        adj = (adj + adj.transpose(0, 1)) * 0.5

        # Align features
        X = claim_features.reindex(claim_ids).fillna(0.0).values
        X_tensor = torch.tensor(X, dtype=torch.float32)

        model = _SimpleGCN(input_dim=X_tensor.shape[1], hidden_dim=hidden_dim, output_dim=out_dim)
        with torch.no_grad():
            embeddings = model(X_tensor, adj).numpy()

        emb_df = pd.DataFrame(embeddings, index=claim_ids, columns=[f"gnn_emb_{i}" for i in range(out_dim)])
        emb_df.insert(0, "claim_id", claim_ids)
        return emb_df

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def get_connected_claims(self, entity_name: str) -> List[str]:
        if entity_name not in self.G:
            return []
        return [
            n
            for n in self.G.neighbors(entity_name)
            if self.G.nodes[n].get("type") == "claim"
        ]

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for _, data in self.G.nodes(data=True):
            node_type = data.get("type", "unknown")
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts

    def to_serializable(self) -> Dict[str, list]:
        nodes = [{"id": n, **d} for n, d in self.G.nodes(data=True)]
        edges = [{"source": u, "target": v, **d} for u, v, d in self.G.edges(data=True)]
        return {"nodes": nodes, "edges": edges}


class _SimpleGCN(nn.Module):
    """Two-hop message passing for lightweight structural embeddings."""

    def __init__(self, input_dim: int, hidden_dim: int = 32, output_dim: int = 16):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        h = self._aggregate(adj, x)
        h = F.relu(self.fc1(h))
        h = self._aggregate(adj, h)
        return self.fc2(h)

    @staticmethod
    def _aggregate(adj: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
        # Normalize adjacency for stability
        deg = torch.sparse.sum(adj, dim=1).to_dense()
        deg_inv_sqrt = torch.pow(deg + 1e-8, -0.5)
        D_inv_sqrt = torch.diag(deg_inv_sqrt)
        dense_adj = adj.to_dense()
        norm_adj = D_inv_sqrt @ dense_adj @ D_inv_sqrt
        return norm_adj @ features


def build_graph(claims: Sequence[dict]) -> GraphEngine:
    """
    Convenience API to build and return a populated GraphEngine.
    """
    engine = GraphEngine()
    engine.build_graph(claims)
    return engine
