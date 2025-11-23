# RiskChain Intelligence API

FastAPI backend for insurance fraud detection with database storage.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python run.py
```

The server will start at `http://localhost:8000`

### 3. Access the Form

Open your browser and go to:
- **Form UI**: `http://localhost:8000/`
- **API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## API Endpoints

### POST `/api/claims`
Create a new claim from form data.

**Request Body:**
```json
{
  "claimant_name": "John Smith",
  "doctor": "Dr. Chen",
  "lawyer": "Attorney Rodriguez",
  "ip_address": "192.168.1.100",
  "accident_type": "Car Accident",
  "description": "Rear-end collision",
  "claim_date": "2024-01-15",
  "missing_docs": ["police_report", "medical_records"],
  "urgency": 3,
  "policy_number": "POL-12345",
  "claim_amount": 5000.00
}
```

**Response:**
```json
{
  "id": 1,
  "claim_id": "C12345678",
  "claimant_name": "John Smith",
  "doctor": "Dr. Chen",
  "lawyer": "Attorney Rodriguez",
  "ip_address": "192.168.1.100",
  "risk_score": 45,
  "risk_category": "medium",
  "claim_data_json": { ... },
  "created_at": "2024-01-15T10:30:00"
}
```

### GET `/api/claims`
Get all claims (with pagination).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

### GET `/api/claims/{claim_id}`
Get a specific claim by ID.

### GET `/api/stats`
Get aggregated statistics about claims and graph.

## Database Schema

The `claims` table stores:

- **Structured Fields** (for easy querying):
  - `claim_id` (unique)
  - `claimant_name`
  - `doctor`
  - `lawyer`
  - `ip_address`
  - `accident_type`
  - `claim_date`
  - `risk_score`
  - `risk_category`

- **JSON Storage**:
  - `claim_data_json` - All form fields stored as JSON
  - `missing_docs` - Array of missing documents

- **Metadata**:
  - `created_at`, `updated_at`
  - `summary` (for AI-generated summaries)

## Form Fields

The form includes 8+ fields:

1. **Claimant Name** (required)
2. **Doctor** (required)
3. **Lawyer/Attorney** (required)
4. **IP Address** (required)
5. **Accident Type** (optional)
6. **Description** (optional)
7. **Claim Date** (optional)
8. **Missing Documents** (checkboxes)
9. **Urgency Level** (1-5, optional)
10. **Policy Number** (optional)
11. **Claim Amount** (optional)

## Integration with Graph Service

When a claim is submitted:

1. Form data is converted to JSON
2. Claim is added to the graph
3. Risk score is calculated based on connections
4. Everything is stored in the database

## Frontend Integration

The API is CORS-enabled and ready for frontend integration:

```javascript
// Example: Submit claim from frontend
const response = await fetch('http://localhost:8000/api/claims', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    claimant_name: 'John Smith',
    doctor: 'Dr. Chen',
    lawyer: 'Attorney Rodriguez',
    ip_address: '192.168.1.100',
    // ... other fields
  })
});

const result = await response.json();
console.log('Risk Score:', result.risk_score);
```

## Database Location

SQLite database file: `riskchain.db` (created automatically in project root)

