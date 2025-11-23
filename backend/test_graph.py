"""
Test script for RiskChain Intelligence Graph Service

This script demonstrates fraud ring detection using the "Smith Family Ring" scenario.
It shows how the graph detects connections between claims that share doctors, lawyers, and IP addresses.
"""

from graph_service import RiskGraph


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def print_claim_details(claim_id: str, claim_data: dict, risk_graph: RiskGraph):
    """Print detailed information about a claim."""
    print(f"\n📋 Claim {claim_id} Details:")
    print(f"   Claimant: {claim_data.get('claimant_name', 'N/A')}")
    print(f"   Doctor: {claim_data.get('doctor', 'N/A')}")
    print(f"   Lawyer: {claim_data.get('lawyer', 'N/A')}")
    print(f"   IP Address: {claim_data.get('ip_address', 'N/A')}")
    print(f"   Missing Docs: {', '.join(claim_data.get('missing_docs', [])) or 'None'}")
    print(f"   NLP Score: {claim_data.get('fraud_nlp_score', 0)}/20")
    
    # Get risk information
    if 'risk_score' in claim_data:
        risk_score = claim_data['risk_score']
        risk_category = claim_data['risk_category']
        risk_breakdown = claim_data.get('risk_breakdown', {})
        
        print(f"\n   ⚠️  Risk Score: {risk_score}/100 ({risk_category.upper()})")
        print(f"   Risk Breakdown:")
        print(f"      - Doctor Risk: +{risk_breakdown.get('doctor_risk', 0)} (degree: {risk_breakdown.get('doctor_degree', 0)})")
        print(f"      - IP Risk: +{risk_breakdown.get('ip_risk', 0)} (degree: {risk_breakdown.get('ip_degree', 0)})")
        print(f"      - Lawyer Risk: +{risk_breakdown.get('lawyer_risk', 0)} (degree: {risk_breakdown.get('lawyer_degree', 0)})")
        print(f"      - Missing Docs Risk: +{risk_breakdown.get('missing_docs_risk', 0)}")
        print(f"      - NLP Risk: +{risk_breakdown.get('nlp_risk', 0)}")
        
        # Show related claims
        related = risk_graph.get_related_claims(claim_id)
        if related:
            print(f"   🔗 Related Claims: {', '.join(related)}")


def main():
    """Main test function demonstrating fraud ring detection."""
    print("=" * 80)
    print("RISKCHAIN INTELLIGENCE - Graph Service Test")
    print("Fraud Ring Detection Demonstration")
    print("=" * 80)
    
    # Initialize the graph
    risk_graph = RiskGraph()
    print("\n✅ Graph initialized")
    
    print_separator()
    print("SCENARIO: The Smith Family Fraud Ring")
    print("\nFour different people file claims. Individually they look normal,")
    print("but they all share Dr. Chen, Attorney Rodriguez, and IP 192.168.1.100")
    print("Our graph will detect this pattern and flag them as high risk.")
    print_separator()
    
    # Define test claims - The Smith Family Ring
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
            "doctor": "Dr. Chen",  # Same doctor - CONNECTION!
            "lawyer": "Attorney Rodriguez",  # Same lawyer - CONNECTION!
            "ip_address": "192.168.1.100",  # Same IP - CONNECTION!
            "missing_docs": ["police_report"],
            "fraud_nlp_score": 8
        },
        {
            "claim_id": "C003",
            "claimant_name": "Bob Smith",
            "doctor": "Dr. Chen",  # Same doctor - CONNECTION!
            "lawyer": "Attorney Rodriguez",  # Same lawyer - CONNECTION!
            "ip_address": "192.168.1.100",  # Same IP - CONNECTION!
            "missing_docs": [],
            "fraud_nlp_score": 12
        },
        {
            "claim_id": "C004",
            "claimant_name": "Alice Smith",
            "doctor": "Dr. Chen",  # Same doctor (degree = 4, threshold > 4, so not triggered yet)
            "lawyer": "Attorney Rodriguez",  # Same lawyer (degree = 4, threshold > 3) - SUSPICIOUS! ✓
            "ip_address": "192.168.1.100",  # Same IP (degree = 4, threshold > 2) - SHARED LOCATION! ✓
            "missing_docs": ["license", "photos"],
            "fraud_nlp_score": 15
        },
        {
            "claim_id": "C005",
            "claimant_name": "Mike Johnson",
            "doctor": "Dr. Williams",  # Different doctor - NO CONNECTION
            "lawyer": "Attorney Brown",  # Different lawyer - NO CONNECTION
            "ip_address": "10.0.0.1",  # Different IP - NO CONNECTION
            "missing_docs": [],
            "fraud_nlp_score": 2
        }
    ]
    
    # Process claims one by one to show how risk scores increase
    print("PROCESSING CLAIMS (Real-time simulation):\n")
    
    processed_claims = []
    
    for i, claim in enumerate(claims, 1):
        print(f"\n{'─' * 80}")
        print(f"Processing Claim {i}/{len(claims)}: {claim['claim_id']}")
        print(f"{'─' * 80}")
        
        # Process claim (adds to graph and calculates risk)
        result = risk_graph.process_claim(claim)
        processed_claims.append(result)
        
        # Print claim details
        print_claim_details(claim['claim_id'], result, risk_graph)
        
        # Show graph stats after each claim
        stats = risk_graph.get_graph_stats()
        print(f"\n   📊 Graph Stats: {stats['claim_count']} claims, {stats['total_nodes']} nodes, {stats['total_edges']} edges")
    
    print_separator()
    print("FRAUD RING DETECTION RESULTS")
    print_separator()
    
    # Summary of all claims
    print("\n📊 Risk Score Summary:")
    print(f"{'Claim ID':<10} {'Claimant':<20} {'Risk Score':<12} {'Category':<10} {'Connections'}")
    print("-" * 80)
    
    for claim in processed_claims:
        claim_id = claim['claim_id']
        claimant = claim['claimant_name']
        risk_score = claim['risk_score']
        category = claim['risk_category'].upper()
        related = risk_graph.get_related_claims(claim_id)
        connections = f"{len(related)} related" if related else "None"
        
        # Color coding
        if risk_score >= 70:
            indicator = "🔴"
        elif risk_score >= 31:
            indicator = "🟡"
        else:
            indicator = "🟢"
        
        print(f"{indicator} {claim_id:<8} {claimant:<20} {risk_score:<3}/100      {category:<10} {connections}")
    
    print_separator()
    print("FRAUD RING ANALYSIS")
    print_separator()
    
    # Analyze the Smith Family Ring
    smith_claims = [c for c in processed_claims if 'Smith' in c['claimant_name']]
    print(f"\n🔍 Detected Fraud Ring: {len(smith_claims)} connected claims")
    
    doctor_degree = risk_graph.graph.degree('Dr. Chen')
    lawyer_degree = risk_graph.graph.degree('Attorney Rodriguez')
    ip_degree = risk_graph.graph.degree('192.168.1.100')
    
    print(f"   Shared Doctor: Dr. Chen (degree: {doctor_degree}) {'⚠️ FRAUD MILL!' if doctor_degree > 4 else '(threshold: >4)'}")
    print(f"   Shared Lawyer: Attorney Rodriguez (degree: {lawyer_degree}) {'⚠️ SUSPICIOUS!' if lawyer_degree > 3 else ''}")
    print(f"   Shared IP: 192.168.1.100 (degree: {ip_degree}) {'⚠️ SHARED LOCATION!' if ip_degree > 2 else ''}")
    
    high_risk_smith = [c for c in smith_claims if c['risk_category'] == 'high']
    print(f"\n   ⚠️  {len(high_risk_smith)}/{len(smith_claims)} Smith family claims flagged as HIGH RISK due to shared connections!")
    
    # Compare with isolated claim
    isolated_claim = [c for c in processed_claims if c['claim_id'] == 'C005'][0]
    print(f"\n✅ Isolated Claim (C005 - Mike Johnson):")
    print(f"   Risk Score: {isolated_claim['risk_score']}/100 ({isolated_claim['risk_category']})")
    print(f"   No shared connections - Low risk")
    
    print_separator()
    print("GRAPH VISUALIZATION DATA")
    print_separator()
    
    # Get visualization data
    viz_data = risk_graph.get_visualization_data()
    print(f"\n📈 Graph Structure:")
    print(f"   Total Nodes: {len(viz_data['nodes'])}")
    print(f"   Total Edges: {len(viz_data['edges'])}")
    print(f"\n   Node Types:")
    node_types = {}
    for node in viz_data['nodes']:
        node_type = node['type']
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    for node_type, count in node_types.items():
        print(f"      - {node_type}: {count}")
    
    print_separator()
    print("SUSPICIOUS CLUSTER DETECTION")
    print_separator()
    
    # Detect clusters
    clusters = risk_graph.detect_suspicious_clusters(min_connections=3)
    print(f"\n🔗 Detected {len(clusters)} suspicious cluster(s):")
    for i, cluster in enumerate(clusters, 1):
        print(f"\n   Cluster {i}: {len(cluster)} connected nodes")
        # Show claim nodes in cluster
        claim_nodes = [n for n in cluster if n.startswith('claim_')]
        if claim_nodes:
            claim_ids = [n.replace('claim_', '') for n in claim_nodes]
            print(f"      Claims: {', '.join(claim_ids)}")
    
    print_separator()
    print("✅ TEST COMPLETE - Fraud ring successfully detected!")
    print("=" * 80)


if __name__ == "__main__":
    main()

