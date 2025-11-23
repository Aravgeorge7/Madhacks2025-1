# RiskChain Intelligence

**Insurance Fraud Detection & Risk Analysis System**

RiskChain Intelligence is an AI-powered insurance fraud detection platform that uses graph network analysis to identify fraud rings and calculate real-time risk scores for insurance claims.

## Overview

Traditional fraud detection systems analyze claims in isolation. RiskChain builds a **connection graph** across all claims to find hidden patterns - shared doctors, lawyers, IP addresses, and other suspicious connections that indicate organized fraud rings.

### Key Features

- **Graph-Based Fraud Detection**: NetworkX-powered connection analysis
- **Real-Time Risk Scoring**: 0-100 risk score calculated instantly
- **Modern Dashboard**: Next.js frontend with real-time updates
- **Comprehensive Database**: SQLite with 350+ pre-loaded claims
- **Claim Submission Form**: Full-featured form matching industry standards
- **Auto-Refresh**: Dashboard updates automatically when new claims are submitted

## Architecture

```
RiskChain Intelligence
├── Frontend (Next.js + TypeScript)
│   ├── Landing Page (Employee/Claimant selection)
│   ├── Dashboard (Employee portal - view claims)
│   └── Form Page (Claimant portal - submit claims)
│
├── Backend (FastAPI + Python)
│   ├── Graph Service (NetworkX fraud detection)
│   ├── Database (SQLite + SQLAlchemy)
│   └── API Endpoints (REST API)
│
└── Database
    └── SQLite (riskchain.db with 350 claims)
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Madhacks2025-1
   ```

2. **Set up Backend**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Initialize database (if not already present)
   cd backend
   python -c "from database import init_db; init_db()"
   ```

3. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   source ../venv/bin/activate
   python run.py
   ```
   Backend runs on: `http://localhost:8000`

2. **Start Frontend Server**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on: `http://localhost:3000`

3. **Access the Application**
   - Open `http://localhost:3000` in your browser
   - Choose "Employee Portal" or "Submit a Claim"

## Project Structure

```
Madhacks2025-1/
├── backend/
│   ├── main.py              # FastAPI application & routes
│   ├── database.py           # SQLAlchemy models & DB setup
│   ├── models.py             # Pydantic validation models
│   ├── graph_service.py      # NetworkX fraud detection logic
│   ├── import_csv_data.py    # CSV data import script
│   ├── run.py                # Server startup script
│   └── riskchain.db          # SQLite database (350 claims)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── dashboard/        # Employee dashboard
│   │   ├── form/             # Claim submission form
│   │   └── graph/            # Graph visualization
│   ├── components/           # React components
│   └── types/                # TypeScript types
│
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Risk Scoring Algorithm

The risk score (0-100) is calculated based on graph connections:

| Factor | Points | Condition |
|--------|--------|-----------|
| **Doctor Fraud Mill** | +40 | Doctor appears in > 4 claims |
| **Shared IP Address** | +25 | IP appears in > 2 claims |
| **Lawyer Pattern** | +15 | Lawyer appears in > 3 claims |
| **Missing Documents** | +10 | Required docs missing |
| **NLP Fraud Score** | +0-10 | AI analysis (future) |

**Risk Categories:**
- **Low Risk**: 0-30 points
- **Medium Risk**: 31-69 points
- **High Risk**: 70-100 points

See `backend/RISK_SCORING.md` for detailed documentation.

## Database Schema

The database stores claims with:
- **Structured Fields**: Policy number, dates, vehicle info, etc.
- **JSON Storage**: Complete form data in `claim_data_json`
- **Graph Connections**: Doctors, lawyers, IP addresses indexed
- **Risk Metrics**: Risk score, category, fraud indicators

See `backend/DATABASE_SETUP.md` for setup instructions.

## API Endpoints

### Claim Management
- `POST /api/claims` - Submit new claim
- `GET /api/claims` - Get all claims (filtered by status)
- `GET /api/claims/{claim_id}` - Get specific claim
- `GET /api/stats` - Get aggregated statistics

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Frontend Routes

- `/` - Landing page (Employee/Claimant selection)
- `/dashboard` - Employee dashboard (view claims)
- `/form` - Claim submission form
- `/graph` - Graph visualization (future)

## Real-Time Updates

The dashboard automatically:
- Refreshes every 5 seconds to show new claims
- Updates instantly when a claim is submitted
- Works across multiple browser tabs

## Testing

### Test Graph Service
```bash
cd backend
python test_graph.py
```

### Import CSV Data
```bash
cd backend
python import_csv_data.py ../car_insurance_training_dataset_with_images.csv
```

## Dependencies

### Backend
- FastAPI - Web framework
- NetworkX - Graph analysis
- SQLAlchemy - Database ORM
- Pydantic - Data validation
- Uvicorn - ASGI server

### Frontend
- Next.js 16 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- React Flow - Graph visualization

## Development

### Branch Structure
- `main` - Production-ready code
- `feature/graph-logic` - Graph & algorithms feature branch
- `frontend` - Frontend development branch

### Adding New Claims
Claims can be submitted via:
1. Web form at `/form`
2. API endpoint `POST /api/claims`
3. CSV import script

## Form Fields

The claim submission form includes:
- Policy information
- Accident details (date, time, location)
- Claimant information
- Vehicle details
- Damage and injury information
- Service providers (lawyer, medical provider)
- Additional documentation

All fields are stored in the database as both structured columns and JSON.

## Fraud Detection

The system detects:
- **Fraud Mills**: Doctors/lawyers handling too many claims
- **Shared Locations**: Multiple claims from same IP
- **Suspicious Patterns**: Unusual connection clusters
- **Missing Documentation**: Incomplete claim submissions

## Statistics

Current database contains:
- **350 claims** pre-loaded from CSV
- **Graph connections** across all entities
- **Risk scores** calculated for each claim
- **Real-time updates** when new claims are submitted

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of MadHacks 2025 hackathon.

## Links

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard
- **Form**: http://localhost:3000/form

## Documentation

- `backend/API_README.md` - API documentation
- `backend/DATABASE_SETUP.md` - Database setup guide
- `backend/RISK_SCORING.md` - Risk scoring algorithm details

## Future Enhancements

- AI/NLP analysis of claim descriptions
- Machine learning models for fraud prediction
- Email integration for automatic claim processing
- Advanced graph visualization
- Historical pattern analysis
- Geographic clustering detection

---

**Built for MadHacks 2025**
