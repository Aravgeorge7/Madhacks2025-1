# Risk Score Calculation

## Overview

The risk score is calculated using a **graph-based fraud detection algorithm** that analyzes connections between claims, doctors, lawyers, and IP addresses to identify potential fraud rings.

## How It Works

### 1. **Graph Construction**
When a claim is submitted, it's added to a NetworkX graph with the following connections:
- **Claim → Doctor** (medical provider)
- **Claim → Lawyer** (attorney)
- **Claim → IP Address** (submission location)
- **Claimant → Claim** (person who filed)

### 2. **Risk Score Calculation**

The risk score (0-100) is calculated based on **graph connections** and other factors:

#### Scoring Breakdown:

| Factor | Points | Condition |
|--------|--------|-----------|
| **Doctor Fraud Mill** | +40 | If doctor appears in **> 4 claims** (suspicious pattern) |
| **Shared IP Address** | +25 | If IP address appears in **> 2 claims** (same location) |
| **Lawyer Pattern** | +15 | If lawyer appears in **> 3 claims** (suspicious pattern) |
| **Missing Documents** | +10 | If required documents are missing |
| **NLP Fraud Score** | +0-10 | Based on AI analysis (0-20 scaled to 0-10) |

**Maximum Score:** 100 (capped)

### 3. **Risk Categories**

Based on the calculated score:

- **Low Risk:** 0-30 points
- **Medium Risk:** 31-69 points  
- **High Risk:** 70-100 points

## Example Scenarios

### Scenario 1: Low Risk (Score: 0)
- New doctor (first claim)
- Unique IP address
- New lawyer
- All documents present
- **Result:** ✅ Low risk

### Scenario 2: Medium Risk (Score: 40)
- Doctor appears in 5 claims (fraud mill detected)
- Unique IP address
- New lawyer
- All documents present
- **Result:** ⚠️ Medium risk

### Scenario 3: High Risk (Score: 80)
- Doctor appears in 6 claims (+40)
- IP address appears in 3 claims (+25)
- Lawyer appears in 4 claims (+15)
- **Result:** 🚨 High risk - Potential fraud ring!

## Code Flow

### When a Claim is Submitted:

1. **Form Submission** → `POST /api/claims`
2. **Graph Processing** → `risk_graph.process_claim(claim_data)`
   - Adds claim to graph
   - Calculates risk score
   - Returns risk category
3. **Database Storage** → Risk score saved with claim

### Key Functions:

```python
# Main processing function
risk_graph.process_claim(claim_dict)
  → add_claim()          # Add to graph
  → calculate_risk_score() # Calculate score
  → get_risk_category()   # Get category (low/medium/high)
```

## Real-Time Detection

The system detects fraud rings in real-time:

**"Smith Family Ring" Example:**
- 4 different people file claims
- They all use **Dr. Chen** (5+ claims)
- They all use **Attorney Rodriguez** (4+ claims)  
- They all use the **same IP address** (3+ claims)
- **Result:** High risk score (70+) - Fraud ring detected! 🚨

## Current Implementation

- **Location:** `backend/graph_service.py`
- **Method:** `calculate_risk_score()`
- **Called from:** `main.py` → `create_claim()` endpoint
- **Graph Library:** NetworkX

## Future Enhancements

- AI/NLP analysis of claim descriptions
- Machine learning models
- Historical pattern analysis
- Geographic clustering detection

