from typing import Dict, List

import networkx as nx
import pandas as pd


class GraphFeatures:
    """
    Computes graph-derived features and graph risk contributions.
    """

    def __init__(self, graph_engine):
        self.engine = graph_engine
        self.G = graph_engine.G
        self._degree_centrality = nx.degree_centrality(self.G) if self.G.number_of_nodes() else {}
        self._betweenness = nx.betweenness_centrality(self.G) if self.G.number_of_nodes() else {}
        self._components = list(nx.connected_components(self.G))
        self._component_labels = self._build_component_labels()

    def _build_component_labels(self) -> Dict[str, int]:
        labels = {}
        for idx, comp in enumerate(self._components):
            for node in comp:
                labels[node] = idx
        return labels

    # ------------------------------------------------------------------ #
    # Feature computation
    # ------------------------------------------------------------------ #
    def _shared_entity_count(self, claim_id: str, node_type: str) -> int:
        total = 0
        for nbr in self.G.neighbors(claim_id):
            if self.G.nodes[nbr].get("type") == node_type:
                total += len([c for c in self.G.neighbors(nbr) if self.G.nodes[c].get("type") == "claim"]) - 1
        return max(total, 0)

    def _similarity_edge_count(self, claim_id: str) -> int:
        return sum(1 for _, _, data in self.G.edges(claim_id, data=True) if str(data.get("relation", "")).startswith("similar_"))

    def compute_features_for_claims(self, claims: List[dict]) -> pd.DataFrame:
        rows = []
        for claim in claims:
            cid = claim["claim_id"]
            rows.append(
                {
                    "claim_id": cid,
                    "graph_degree_centrality": self._degree_centrality.get(cid, 0.0),
                    "graph_betweenness": self._betweenness.get(cid, 0.0),
                    "graph_cluster": self._component_labels.get(cid, -1),
                    "shared_ips": self._shared_entity_count(cid, "ip"),
                    "shared_doctors": self._shared_entity_count(cid, "provider"),
                    "shared_lawyers": self._shared_entity_count(cid, "lawyer"),
                    "similarity_edge_count": self._similarity_edge_count(cid),
                    "graph_risk_score": self.compute_graph_risk(claim),
                }
            )
        return pd.DataFrame(rows).set_index("claim_id")

    # ------------------------------------------------------------------ #
    # Risk scoring rules (0-30)
    # ------------------------------------------------------------------ #
    def _degree(self, node: str) -> int:
        try:
            return self.G.degree(node)
        except Exception:
            return 0

    def provider_volume_score(self, provider: str) -> int:
        if not provider or provider not in self.G:
            return 0
        count = self._degree(provider)
        if count >= 20:
            return 12
        if count >= 10:
            return 8
        if count >= 5:
            return 5
        return 0

    def lawyer_density_score(self, lawyer: str) -> int:
        if not lawyer or lawyer not in self.G:
            return 0
        count = self._degree(lawyer)
        if count >= 25:
            return 12
        if count >= 10:
            return 7
        if count >= 5:
            return 4
        return 0

    def provider_lawyer_combo_score(self, provider: str, lawyer: str) -> int:
        if not provider or not lawyer:
            return 0
        if provider not in self.G or lawyer not in self.G:
            return 0
        provider_claims = {n for n in self.G.neighbors(provider) if self.G.nodes[n].get("type") == "claim"}
        lawyer_claims = {n for n in self.G.neighbors(lawyer) if self.G.nodes[n].get("type") == "claim"}
        overlap = len(provider_claims & lawyer_claims)
        if overlap >= 15:
            return 12
        if overlap >= 7:
            return 8
        if overlap >= 3:
            return 4
        return 0

    def ip_reuse_score(self, claim: dict) -> int:
        ip = claim.get("ip_address")
        cid = claim["claim_id"]
        if not ip or ip not in self.G:
            return 0
        claims = [n for n in self.G.neighbors(ip) if self.G.nodes[n].get("type") == "claim" and n != cid]
        if len(claims) >= 10:
            return 8
        if len(claims) >= 5:
            return 5
        if len(claims) >= 2:
            return 3
        return 0

    def compute_graph_risk(self, claim: dict) -> int:
        provider = claim.get("medical_provider_name")
        lawyer = claim.get("lawyer_name")
        total = 0
        total += self.provider_volume_score(provider)
        total += self.lawyer_density_score(lawyer)
        total += self.provider_lawyer_combo_score(provider, lawyer)
        total += self.ip_reuse_score(claim)
        return min(total, 30)
