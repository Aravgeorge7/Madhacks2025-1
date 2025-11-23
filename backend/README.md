# RiskChain Intelligence - Graph Service

Graph-based fraud detection service for insurance claims using NetworkX.

## Overview

The `RiskGraph` class builds a connection graph across all insurance claims to detect fraud rings. Traditional fraud systems look at claims in isolation, but RiskChain identifies hidden connections through shared doctors, lawyers, and IP addresses.

## Key Features

- **Real-time Claim Processing**: Process claims as they arrive from emails
- **Fraud Ring Detection**: Automatically detect suspicious patterns and connections
- **Risk Scoring**: Calculate fraud risk scores (0-100) based on graph connections
- **Visualization Ready**: Export graph data in React Flow compatible format
- **Cluster Detection**: Identify suspicious clusters of connected claims

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from graph_service import RiskGraph

# Initialize graph
risk_graph = RiskGraph()

# Process a claim (adds to graph and calculates risk)
claim = {
    "claim_id": "C001",
    "claimant_name": "John Smith",
    "doctor": "Dr. Chen",
    "lawyer": "Attorney Rodriguez",
    "ip_address": "192.168.1.100",
    "missing_docs": [],
    "fraud_nlp_score": 5
}

result = risk_graph.process_claim(claim)
print(f"Risk Score: {result['risk_score']}/100 ({result['risk_category']})")
```

## Running Tests

```bash
cd backend
python test_graph.py
```

This will demonstrate the "Smith Family Fraud Ring" scenario where 4 different people file claims sharing the same doctor, lawyer, and IP address.

## Risk Scoring Logic

The risk score (0-100) is calculated based on:

- **+40 points**: Doctor node degree > 4 (fraud mill detection)
- **+25 points**: IP address degree > 2 (shared location)
- **+15 points**: Lawyer node degree > 3 (suspicious pattern)
- **+10 points**: Missing required documents
- **+10 points**: NLP-based fraud score (0-20 scaled to 0-10)

**Risk Categories:**
- **Low**: 0-30 (Green)
- **Medium**: 31-69 (Yellow)
- **High**: 70-100 (Red)

## API Reference

### `RiskGraph`

#### `process_claim(claim_dict) -> dict`
Process a claim end-to-end: add to graph and calculate risk score. **Recommended for real-time processing.**

**Returns:** Claim dict with added `risk_score`, `risk_category`, and `risk_breakdown`

#### `add_claim(claim_dict) -> None`
Add a claim and its relationships to the graph.

#### `calculate_risk_score(claim_dict, graph=None) -> int`
Calculate fraud risk score for a claim based on graph connections.

#### `get_visualization_data() -> dict`
Get graph data formatted for React Flow visualization.

#### `get_related_claims(claim_id) -> List[str]`
Get list of related claim IDs that share connections.

#### `get_graph_stats() -> dict`
Get statistics about the current graph state.

## Real-time Email Processing

The graph service is designed to work with real-time email processing:

```python
# When an email arrives:
email_data = extract_claim_from_email(email)

# Process immediately:
result = risk_graph.process_claim(email_data)

# Check if high risk:
if result['risk_category'] == 'high':
    flag_for_review(result)
```

## Example: Fraud Ring Detection

```python
# Four claims sharing connections
claims = [
    {"claim_id": "C001", "doctor": "Dr. Chen", "lawyer": "Attorney Rodriguez", "ip_address": "192.168.1.100"},
    {"claim_id": "C002", "doctor": "Dr. Chen", "lawyer": "Attorney Rodriguez", "ip_address": "192.168.1.100"},
    {"claim_id": "C003", "doctor": "Dr. Chen", "lawyer": "Attorney Rodriguez", "ip_address": "192.168.1.100"},
    {"claim_id": "C004", "doctor": "Dr. Chen", "lawyer": "Attorney Rodriguez", "ip_address": "192.168.1.100"},
]

# Process all claims
for claim in claims:
    result = risk_graph.process_claim(claim)
    print(f"{result['claim_id']}: {result['risk_score']}/100")

# All will show HIGH RISK due to shared connections!
```

## Integration with FastAPI

```python
from fastapi import FastAPI
from graph_service import RiskGraph

app = FastAPI()
risk_graph = RiskGraph()

@app.post("/api/process-email")
async def process_email(email_data: dict):
    result = risk_graph.process_claim(email_data)
    return result
```

