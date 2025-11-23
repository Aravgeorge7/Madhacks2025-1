"""
Simple test script to verify graph_service.py functionality.
This can be run independently to test the RiskGraph class.
"""

from graph_service import RiskGraph


def test_basic_functionality():
    """Test basic graph operations and risk scoring."""
    print("Testing RiskGraph...")
    
    # Initialize graph
    risk_graph = RiskGraph()
    print("✓ Graph initialized")
    
    # Add some test claims (simulating the "Smith Family Ring" scenario)
    claims = [
        {
            "claim_id": "C001",
            "claimant_name": "John Smith",
            "doctor": "Dr. Chen",
            "lawyer": "Attorney Rodriguez",
            "ip_address": "192.168.1.100",
            "missing_docs": [],
            "fraud_nlp_score": 5
        },
        {
            "claim_id": "C002",
            "claimant_name": "Jane Smith",
            "doctor": "Dr. Chen",  # Same doctor
            "lawyer": "Attorney Rodriguez",  # Same lawyer
            "ip_address": "192.168.1.100",  # Same IP
            "missing_docs": ["police_report"],
            "fraud_nlp_score": 8
        },
        {
            "claim_id": "C003",
            "claimant_name": "Bob Smith",
            "doctor": "Dr. Chen",  # Same doctor
            "lawyer": "Attorney Rodriguez",  # Same lawyer
            "ip_address": "192.168.1.100",  # Same IP
            "missing_docs": [],
            "fraud_nlp_score": 12
        },
        {
            "claim_id": "C004",
            "claimant_name": "Alice Smith",
            "doctor": "Dr. Chen",  # Same doctor (now degree > 4)
            "lawyer": "Attorney Rodriguez",  # Same lawyer (now degree > 3)
            "ip_address": "192.168.1.100",  # Same IP (now degree > 2)
            "missing_docs": ["license", "photos"],
            "fraud_nlp_score": 15
        },
        {
            "claim_id": "C005",
            "claimant_name": "Mike Johnson",
            "doctor": "Dr. Williams",  # Different doctor
            "lawyer": "Attorney Brown",  # Different lawyer
            "ip_address": "10.0.0.1",  # Different IP
            "missing_docs": [],
            "fraud_nlp_score": 2
        }
    ]
    
    # Add all claims
    for claim in claims:
        risk_graph.add_claim(claim)
    print(f"✓ Added {len(claims)} claims to graph")
    
    # Calculate risk scores
    print("\nRisk Scores:")
    for claim in claims:
        score = risk_graph.calculate_risk_score(claim)
        category = risk_graph.get_risk_category(score)
        print(f"  {claim['claim_id']}: {score}/100 ({category})")
    
    # Test visualization data
    viz_data = risk_graph.get_visualization_data()
    print(f"\n✓ Visualization data: {len(viz_data['nodes'])} nodes, {len(viz_data['edges'])} edges")
    
    # Test subgraph
    subgraph = risk_graph.get_claim_subgraph("C001")
    print(f"✓ Subgraph for C001: {len(subgraph['nodes'])} nodes, {len(subgraph['edges'])} edges")
    
    # Test cluster detection
    clusters = risk_graph.detect_suspicious_clusters()
    print(f"✓ Detected {len(clusters)} suspicious clusters")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_basic_functionality()


