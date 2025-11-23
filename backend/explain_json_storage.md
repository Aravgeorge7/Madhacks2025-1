# How Form Data is Saved as JSON in Database

## Overview

All form data is saved in **two ways**:
1. **Structured fields** - Individual columns for easy querying (claimant_name, doctor, etc.)
2. **JSON field** - Complete form data stored as JSON in `claim_data_json` column

## Data Flow

### Step 1: Form Submission
When user submits the form, JavaScript collects all form data:

```javascript
// From the form HTML
const formData = new FormData(this);
const data = {};

for (let [key, value] of formData.entries()) {
    if (key === 'missing_docs') {
        if (!data[key]) data[key] = [];
        data[key].push(value);
    } else {
        data[key] = value || null;
    }
}
```

### Step 2: API Endpoint Receives Data
The `/api/claims` endpoint receives the JSON:

```python
@app.post("/api/claims", response_model=ClaimResponse)
async def create_claim(claim_data: ClaimFormData, db: Session = Depends(get_db)):
```

### Step 3: Convert to JSON
The Pydantic model validates and converts to dictionary:

```python
# Convert form data to JSON
claim_json = claim_data.model_dump()  # This creates a Python dict
```

### Step 4: Store in Database
The data is stored in TWO places:

```python
db_claim = Claim(
    # Structured fields (for queries)
    claimant_name=claim_data.claimant_name,
    doctor=claim_data.doctor,
    lawyer=claim_data.lawyer,
    ip_address=claim_data.ip_address,
    accident_type=claim_data.accident_type,
    
    # Complete JSON storage
    claim_data_json=claim_json,  # ALL form data as JSON
    
    # Other fields
    missing_docs=claim_data.missing_docs or []
)
```

## Example JSON Structure

When a form is submitted, the `claim_data_json` field stores:

```json
{
  "claimant_name": "John Michael Smith",
  "policy_number": "POL-2024-12345",
  "accident_type": "Auto Accident - Collision",
  "claim_date": "2024-01-15",
  "description": "Rear-end collision on Highway 101 at 2:30 PM",
  "claim_amount": 5000.00,
  "doctor": "Dr. Sarah Chen, M.D.",
  "medical_facility": "City General Hospital",
  "lawyer": "Attorney Maria Rodriguez, Esq.",
  "ip_address": "192.168.1.100",
  "missing_docs": ["police_report", "medical_records"],
  "urgency": 3
}
```

## Database Schema

The `claims` table has:

```sql
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    claim_id TEXT UNIQUE,
    
    -- Structured fields
    claimant_name TEXT,
    doctor TEXT,
    lawyer TEXT,
    ip_address TEXT,
    accident_type TEXT,
    claim_date DATETIME,
    
    -- JSON storage (stores ALL form data)
    claim_data_json JSON,  -- <-- Complete form data here
    
    -- Risk fields
    risk_score INTEGER,
    risk_category TEXT,
    
    -- Other
    missing_docs JSON,  -- Array of missing documents
    created_at DATETIME,
    updated_at DATETIME
);
```

## Why Both?

- **Structured fields**: Fast queries (e.g., "Find all claims by Dr. Chen")
- **JSON field**: Complete data preservation, flexible for future fields

## Accessing the JSON

```python
# Get claim from database
claim = db.query(Claim).filter(Claim.claim_id == "C12345678").first()

# Access structured field
print(claim.claimant_name)  # "John Michael Smith"

# Access complete JSON
print(claim.claim_data_json)  # Full dictionary with all form data
print(claim.claim_data_json['policy_number'])  # "POL-2024-12345"
print(claim.claim_data_json['description'])  # Full description
```

## Benefits

1. **Flexibility**: Add new form fields without changing database schema
2. **Complete History**: All original form data preserved
3. **Easy Queries**: Structured fields for common searches
4. **Future-Proof**: JSON can store any additional fields later

