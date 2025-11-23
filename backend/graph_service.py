"""
Graph Service for RiskChain Intelligence

This module provides graph-based fraud detection using NetworkX.
It builds a connection graph across claims to detect fraud rings.
"""

from typing import Dict, List, Optional, Any
import networkx as nx


class RiskGraph:
    """
    A graph-based fraud detection system that tracks relationships
    between claims, people, doctors, lawyers, and IP addresses.
    """
    
    def __init__(self):
        """Initialize an empty NetworkX graph."""
        self.graph = nx.Graph()
    
    def add_claim(self, claim_dict: Dict[str, Any]) -> None:
        """
        Add a claim and its relationships to the graph.
        
        Expected claim_dict structure:
        {
            "claim_id": str,
            "claimant_name": str,
            "doctor": str,
            "lawyer": str,
            "ip_address": str,
            "missing_docs": List[str] (optional),
            "fraud_nlp_score": int (optional, 0-20)
        }
        
        Args:
            claim_dict: Dictionary containing claim information
        """
        claim_id = claim_dict.get("claim_id")
        claimant_name = claim_dict.get("claimant_name", "")
        doctor = claim_dict.get("doctor", "")
        lawyer = claim_dict.get("lawyer", "")
        ip_address = claim_dict.get("ip_address", "")
        missing_docs = claim_dict.get("missing_docs", [])
        fraud_nlp_score = claim_dict.get("fraud_nlp_score", 0)
        
        if not claim_id:
            raise ValueError("claim_id is required")
        
        # Create node IDs
        claim_node = f"claim_{claim_id}"
        
        # Add claim node with metadata
        self.graph.add_node(
            claim_node,
            type="claim",
            claim_id=claim_id,
            missing_docs=missing_docs,
            fraud_nlp_score=fraud_nlp_score
        )
        
        # Add person node if claimant name exists
        if claimant_name:
            self.graph.add_node(claimant_name, type="person")
            # Edge: person -> claim (filed)
            self.graph.add_edge(claimant_name, claim_node, relationship="filed")
        
        # Add doctor node if doctor exists
        if doctor:
            self.graph.add_node(doctor, type="doctor")
            # Edge: claim -> doctor (treated_by)
            self.graph.add_edge(claim_node, doctor, relationship="treated_by")
        
        # Add lawyer node if lawyer exists
        if lawyer:
            self.graph.add_node(lawyer, type="lawyer")
            # Edge: claim -> lawyer (represented_by)
            self.graph.add_edge(claim_node, lawyer, relationship="represented_by")
        
        # Add IP address node if IP exists
        if ip_address:
            self.graph.add_node(ip_address, type="ip")
            # Edge: claim -> ip (submitted_from)
            self.graph.add_edge(claim_node, ip_address, relationship="submitted_from")
    
    def calculate_risk_score(self, claim_dict: Dict[str, Any], graph: Optional[nx.Graph] = None) -> int:
        """
        Calculate fraud risk score for a claim based on graph connections.
        
        IMPORTANT: For accurate scoring, the claim should already be added to the graph.
        Use process_claim() for end-to-end processing (add + calculate).
        
        Scoring logic:
        - +40 points: Doctor node degree > 4 (fraud mill)
        - +25 points: IP address degree > 2 (shared location)
        - +15 points: Lawyer node degree > 3 (suspicious pattern)
        - +10 points: Missing required documents
        - +10 points: Based on fraud_nlp_score (0-20 scaled to 0-10)
        
        Args:
            claim_dict: Dictionary containing claim information
            graph: Optional graph to use (defaults to self.graph)
        
        Returns:
            Integer risk score from 0-100
        """
        if graph is None:
            graph = self.graph
        
        score = 0
        doctor = claim_dict.get("doctor", "")
        lawyer = claim_dict.get("lawyer", "")
        ip_address = claim_dict.get("ip_address", "")
        missing_docs = claim_dict.get("missing_docs", [])
        fraud_nlp_score = claim_dict.get("fraud_nlp_score", 0)
        
        # Check doctor connections (fraud mill detection)
        # Note: Degree includes the current claim, so we check > 4 (not >= 4)
        if doctor and doctor in graph:
            doctor_degree = graph.degree(doctor)
            if doctor_degree > 4:
                score += 40
        
        # Check IP address connections (shared location)
        if ip_address and ip_address in graph:
            ip_degree = graph.degree(ip_address)
            if ip_degree > 2:
                score += 25
        
        # Check lawyer connections (suspicious pattern)
        if lawyer and lawyer in graph:
            lawyer_degree = graph.degree(lawyer)
            if lawyer_degree > 3:
                score += 15
        
        # Check for missing documents
        if missing_docs and len(missing_docs) > 0:
            score += 10
        
        # Add NLP-based fraud score (scale 0-20 to 0-10)
        if fraud_nlp_score:
            nlp_contribution = min(10, int(fraud_nlp_score / 2))
            score += nlp_contribution
        
        # Cap score at 100
        return min(100, score)
    
    def process_claim(self, claim_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a claim end-to-end: add to graph and calculate risk score.
        
        This is the recommended method for real-time email processing.
        It adds the claim to the graph first, then calculates the risk score
        based on the updated graph state.
        
        Args:
            claim_dict: Dictionary containing claim information
        
        Returns:
            Dictionary with claim data plus:
            - risk_score: Calculated risk score (0-100)
            - risk_category: "low", "medium", or "high"
            - risk_breakdown: Detailed breakdown of risk factors
        """
        # Add claim to graph first
        self.add_claim(claim_dict)
        
        # Calculate risk score (now that claim is in graph)
        risk_score = self.calculate_risk_score(claim_dict)
        risk_category = self.get_risk_category(risk_score)
        
        # Get risk breakdown for detailed analysis
        risk_breakdown = self._get_risk_breakdown(claim_dict)
        
        return {
            **claim_dict,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "risk_breakdown": risk_breakdown
        }
    
    def _get_risk_breakdown(self, claim_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed breakdown of risk factors for a claim.
        
        Args:
            claim_dict: Dictionary containing claim information
        
        Returns:
            Dictionary with risk factor details
        """
        breakdown = {
            "doctor_risk": 0,
            "ip_risk": 0,
            "lawyer_risk": 0,
            "missing_docs_risk": 0,
            "nlp_risk": 0,
            "doctor_degree": 0,
            "ip_degree": 0,
            "lawyer_degree": 0
        }
        
        doctor = claim_dict.get("doctor", "")
        lawyer = claim_dict.get("lawyer", "")
        ip_address = claim_dict.get("ip_address", "")
        missing_docs = claim_dict.get("missing_docs", [])
        fraud_nlp_score = claim_dict.get("fraud_nlp_score", 0)
        
        if doctor and doctor in self.graph:
            doctor_degree = self.graph.degree(doctor)
            breakdown["doctor_degree"] = doctor_degree
            if doctor_degree > 4:
                breakdown["doctor_risk"] = 40
        
        if ip_address and ip_address in self.graph:
            ip_degree = self.graph.degree(ip_address)
            breakdown["ip_degree"] = ip_degree
            if ip_degree > 2:
                breakdown["ip_risk"] = 25
        
        if lawyer and lawyer in self.graph:
            lawyer_degree = self.graph.degree(lawyer)
            breakdown["lawyer_degree"] = lawyer_degree
            if lawyer_degree > 3:
                breakdown["lawyer_risk"] = 15
        
        if missing_docs and len(missing_docs) > 0:
            breakdown["missing_docs_risk"] = 10
        
        if fraud_nlp_score:
            breakdown["nlp_risk"] = min(10, int(fraud_nlp_score / 2))
        
        return breakdown
    
    def get_risk_category(self, risk_score: int) -> str:
        """
        Get risk category label for a risk score.
        
        Args:
            risk_score: Integer score from 0-100
        
        Returns:
            Risk category: "low", "medium", or "high"
        """
        if risk_score <= 30:
            return "low"
        elif risk_score <= 69:
            return "medium"
        else:
            return "high"
    
    def get_visualization_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get graph data formatted for React Flow visualization.
        
        Returns:
            Dictionary with "nodes" and "edges" lists compatible with React Flow
        """
        nodes = []
        edges = []
        
        # Process all nodes
        for node_id, node_data in self.graph.nodes(data=True):
            node_type = node_data.get("type", "unknown")
            
            # Determine label based on node type
            if node_type == "claim":
                label = f"Claim {node_data.get('claim_id', node_id)}"
            else:
                label = str(node_id)
            
            # Get risk level if it's a claim node
            risk_level = "low"
            if node_type == "claim":
                claim_dict = {
                    "claim_id": node_data.get("claim_id", ""),
                    "doctor": "",
                    "lawyer": "",
                    "ip_address": "",
                    "missing_docs": node_data.get("missing_docs", []),
                    "fraud_nlp_score": node_data.get("fraud_nlp_score", 0)
                }
                # Find connected entities for risk calculation
                neighbors = list(self.graph.neighbors(node_id))
                for neighbor in neighbors:
                    neighbor_data = self.graph.nodes[neighbor]
                    if neighbor_data.get("type") == "doctor":
                        claim_dict["doctor"] = neighbor
                    elif neighbor_data.get("type") == "lawyer":
                        claim_dict["lawyer"] = neighbor
                    elif neighbor_data.get("type") == "ip":
                        claim_dict["ip_address"] = neighbor
                
                risk_score = self.calculate_risk_score(claim_dict)
                risk_level = self.get_risk_category(risk_score)
            
            nodes.append({
                "id": node_id,
                "type": node_type,
                "data": {
                    "label": label,
                    "risk_level": risk_level
                }
            })
        
        # Process all edges
        edge_id_counter = 0
        for source, target, edge_data in self.graph.edges(data=True):
            relationship = edge_data.get("relationship", "connected")
            edges.append({
                "id": f"edge_{edge_id_counter}",
                "source": source,
                "target": target,
                "type": relationship
            })
            edge_id_counter += 1
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_claim_subgraph(self, claim_id: str, hops: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get local subgraph around a specific claim.
        
        Args:
            claim_id: The claim ID to get subgraph for
            hops: Number of hops to include (default: 2)
        
        Returns:
            Dictionary with "nodes" and "edges" for the subgraph
        """
        claim_node = f"claim_{claim_id}"
        
        if claim_node not in self.graph:
            return {"nodes": [], "edges": []}
        
        # Get nodes within specified hops
        subgraph_nodes = {claim_node}
        current_level = {claim_node}
        
        for _ in range(hops):
            next_level = set()
            for node in current_level:
                neighbors = list(self.graph.neighbors(node))
                next_level.update(neighbors)
            subgraph_nodes.update(next_level)
            current_level = next_level
        
        # Create subgraph
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        # Convert to visualization format
        nodes = []
        edges = []
        
        for node_id, node_data in subgraph.nodes(data=True):
            node_type = node_data.get("type", "unknown")
            if node_type == "claim":
                label = f"Claim {node_data.get('claim_id', node_id)}"
            else:
                label = str(node_id)
            
            nodes.append({
                "id": node_id,
                "type": node_type,
                "data": {
                    "label": label,
                    "risk_level": "low"  # Simplified for subgraph
                }
            })
        
        edge_id_counter = 0
        for source, target, edge_data in subgraph.edges(data=True):
            relationship = edge_data.get("relationship", "connected")
            edges.append({
                "id": f"edge_{edge_id_counter}",
                "source": source,
                "target": target,
                "type": relationship
            })
            edge_id_counter += 1
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def detect_suspicious_clusters(self, min_connections: int = 3) -> List[List[str]]:
        """
        Detect suspicious clusters of highly connected nodes.
        
        Uses community detection to find groups of nodes that are
        more connected to each other than to the rest of the graph.
        
        Args:
            min_connections: Minimum number of connections to consider suspicious
        
        Returns:
            List of clusters, where each cluster is a list of node IDs
        """
        if len(self.graph) == 0:
            return []
        
        try:
            # Use greedy modularity communities for clustering
            communities = nx.community.greedy_modularity_communities(self.graph)
            
            suspicious_clusters = []
            for community in communities:
                # Filter communities by minimum connections
                community_list = list(community)
                if len(community_list) >= min_connections:
                    suspicious_clusters.append(community_list)
            
            return suspicious_clusters
        except Exception:
            # Fallback: return empty list if clustering fails
            return []
    
    def get_related_claims(self, claim_id: str) -> List[str]:
        """
        Get list of related claim IDs that share connections (same doctor, lawyer, or IP).
        
        Useful for identifying potential fraud rings around a specific claim.
        
        Args:
            claim_id: The claim ID to find related claims for
        
        Returns:
            List of related claim IDs
        """
        claim_node = f"claim_{claim_id}"
        
        if claim_node not in self.graph:
            return []
        
        related_claims = set()
        
        # Get all neighbors (doctor, lawyer, IP, person)
        neighbors = list(self.graph.neighbors(claim_node))
        
        # For each neighbor, find all connected claims
        for neighbor in neighbors:
            neighbor_neighbors = list(self.graph.neighbors(neighbor))
            for nn in neighbor_neighbors:
                if nn.startswith("claim_") and nn != claim_node:
                    # Extract claim ID from node name
                    related_claim_id = nn.replace("claim_", "")
                    related_claims.add(related_claim_id)
        
        return sorted(list(related_claims))
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current graph state.
        
        Returns:
            Dictionary with graph statistics
        """
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "claim_count": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "claim"]),
            "doctor_count": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "doctor"]),
            "lawyer_count": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "lawyer"]),
            "ip_count": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "ip"]),
            "person_count": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "person"])
        }


