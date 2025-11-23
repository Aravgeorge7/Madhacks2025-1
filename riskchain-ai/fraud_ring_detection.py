import itertools
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List

import networkx as nx
import pandas as pd

from graph_engine.graph_features import GraphFeatures


def detect_fraud_rings(graph_engine) -> Dict[str, list]:
    """
    Analyze a built graph and surface suspicious components + entities.
    Returns a serializable structure consumed by run_demo and API.
    """
    G = graph_engine.G
    gf = GraphFeatures(graph_engine)

    components = list(nx.connected_components(G))
    claim_components = [
        comp for comp in components if any(G.nodes[n].get("type") == "claim" for n in comp)
    ]

    fraud_rings = []
    suspicious_entities = []

    # Component-level analysis
    for comp in claim_components:
        claim_nodes = [n for n in comp if G.nodes[n].get("type") == "claim"]
        if len(claim_nodes) < 3:
            continue

        provider_counts = Counter()
        lawyer_counts = Counter()
        ip_counts = Counter()

        for c in claim_nodes:
            provider_counts.update(_neighbor_entities(G, c, "provider"))
            lawyer_counts.update(_neighbor_entities(G, c, "lawyer"))
            ip_counts.update(_neighbor_entities(G, c, "ip"))

        dominant_provider, prov_freq = provider_counts.most_common(1)[0] if provider_counts else (None, 0)
        dominant_lawyer, law_freq = lawyer_counts.most_common(1)[0] if lawyer_counts else (None, 0)
        dominant_ip, ip_freq = ip_counts.most_common(1)[0] if ip_counts else (None, 0)

        score = 0
        if prov_freq >= 3:
            score += 5
        if law_freq >= 3:
            score += 5
        if ip_freq >= 3:
            score += 5
        if len(claim_nodes) >= 6:
            score += 5
        if score >= 10:
            fraud_rings.append(
                {
                    "claim_count": len(claim_nodes),
                    "claims": claim_nodes,
                    "dominant_provider": dominant_provider,
                    "dominant_lawyer": dominant_lawyer,
                    "dominant_ip": dominant_ip,
                    "score": score,
                }
            )

    # High-degree providers/lawyers/IPs
    for node, data in G.nodes(data=True):
        n_type = data.get("type")
        deg = G.degree(node)
        if n_type in {"provider", "lawyer", "ip"} and deg >= 8:
            suspicious_entities.append(
                {"entity": node, "type": n_type, "degree": deg, "reason": "high_degree"}
            )

    # Bipartite rings (provider + lawyer combination)
    combo_counts = Counter()
    for claim in graph_engine.claim_records.values():
        provider = claim.get("medical_provider_name")
        lawyer = claim.get("lawyer_name")
        if provider and lawyer:
            combo_counts[(provider, lawyer)] += 1
    for (prov, law), freq in combo_counts.items():
        if freq >= 4:
            suspicious_entities.append(
                {
                    "entity": f"{prov} + {law}",
                    "type": "provider_lawyer_combo",
                    "degree": freq,
                    "reason": "repeated_combo",
                }
            )

    # Centrality hotlist
    centrality_sorted = sorted(
        [(n, gf._betweenness.get(n, 0.0)) for n in G.nodes()], key=lambda x: x[1], reverse=True
    )[:10]
    for node, score in centrality_sorted:
        if G.nodes[node].get("type") == "claim":
            continue
        if score > 0:
            suspicious_entities.append(
                {"entity": node, "type": G.nodes[node].get("type"), "degree": G.degree(node), "reason": "central"}
            )

    nodes = [{"id": n, **d} for n, d in G.nodes(data=True)]
    edges = [{"source": u, "target": v, **d} for u, v, d in G.edges(data=True)]

    return {
        "nodes": nodes,
        "edges": edges,
        "clusters": [list(comp) for comp in claim_components],
        "suspicious_entities": suspicious_entities,
        "fraud_rings": fraud_rings,
    }


def _neighbor_entities(G, claim_id: str, entity_type: str) -> List[str]:
    return [
        n
        for n in G.neighbors(claim_id)
        if G.nodes[n].get("type") == entity_type
    ]
