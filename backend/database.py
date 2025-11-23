"""
Database setup and models for RiskChain Intelligence
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./riskchain.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Claim(Base):
    """
    Database model for insurance claims.
    Stores all claim information as JSON and structured fields.
    """
    __tablename__ = "claims"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Auto-generated claim ID
    claim_id = Column(String, unique=True, index=True, nullable=False)
    
    # Structured fields from CSV dataset (for easy querying)
    policy_number = Column(String, index=True)
    claim_submission_date = Column(DateTime)
    accident_date = Column(DateTime)
    accident_time = Column(String)
    accident_location_city = Column(String)
    accident_location_state = Column(String)
    accident_description = Column(Text)
    police_report_filed = Column(Integer, default=0)  # 0 or 1
    loss_type = Column(String, index=True)
    claimant_age = Column(Integer)
    claimant_gender = Column(String)
    claimant_city = Column(String)
    claimant_state = Column(String)
    vehicle_make = Column(String, index=True)
    vehicle_model = Column(String)
    vehicle_year = Column(Integer)
    vehicle_use_type = Column(String)
    vehicle_mileage = Column(Integer)
    damage_severity = Column(String)
    injury_severity = Column(String)
    medical_treatment_received = Column(Integer, default=0)  # 0 or 1
    medical_cost_estimate = Column(Float)
    airbags_deployed = Column(Integer, default=0)  # 0 or 1
    policy_tenure_months = Column(Integer)
    coverage_type = Column(String)
    policy_type = Column(String)
    deductible_amount = Column(Float)
    previous_claims_count = Column(Integer, default=0)
    lawyer_name = Column(String, index=True)
    medical_provider_name = Column(String, index=True)
    repair_shop_name = Column(String)
    reported_by = Column(String)
    photos_url = Column(Text)  # URL to image
    photos_local_path = Column(String)  # Local path after download
    fraud_label = Column(Integer, default=0)  # 0 or 1
    status = Column(String, default="unsettled")
    
    # Legacy fields (kept for compatibility)
    claimant_name = Column(String, index=True)
    doctor = Column(String, index=True)
    lawyer = Column(String, index=True)
    ip_address = Column(String, index=True)
    accident_type = Column(String)
    claim_date = Column(DateTime, default=datetime.utcnow)
    
    # Risk scoring fields
    risk_score = Column(Integer, default=0)
    risk_category = Column(String, default="low")  # low, medium, high
    fraud_nlp_score = Column(Integer, default=0)
    
    # JSON storage for all form data and metadata
    claim_data_json = Column(JSON)  # Stores all form fields as JSON
    
    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI-generated summary (optional)
    summary = Column(Text, nullable=True)
    
    # Missing documents (stored as JSON array)
    missing_docs = Column(JSON, default=list)
    
    def to_dict(self):
        """Convert claim to dictionary with ALL fields from claim_data_json and structured columns."""
        # Start with claim_data_json (contains full form dump)
        json_data = self.claim_data_json.copy() if self.claim_data_json else {}
        
        # Helper function to format datetime
        def format_datetime(dt):
            if dt is None:
                return None
            try:
                return dt.isoformat()
            except:
                return None
        
        # Merge structured database columns on top of claim_data_json
        # This ensures database values override JSON values (database is source of truth for CSV imports)
        result = {
            # Start with JSON data (form submissions)
            **json_data,
            
            # Override with structured database fields (CSV imports and updates)
            "id": str(self.id),
            "claim_id": self.claim_id,
            "policy_number": self.policy_number or json_data.get("policy_number"),
            "claim_submission_date": format_datetime(self.claim_submission_date) or json_data.get("claim_submission_date"),
            "accident_date": format_datetime(self.accident_date) or json_data.get("accident_date"),
            "accident_time": self.accident_time or json_data.get("accident_time"),
            "accident_location_city": self.accident_location_city or json_data.get("accident_location_city"),
            "accident_location_state": self.accident_location_state or json_data.get("accident_location_state"),
            "accident_description": self.accident_description or json_data.get("accident_description"),
            "police_report_filed": self.police_report_filed if self.police_report_filed is not None else json_data.get("police_report_filed"),
            "loss_type": self.loss_type or json_data.get("loss_type"),
            "claimant_name": self.claimant_name or json_data.get("claimant_name"),
            "claimant_age": self.claimant_age if self.claimant_age is not None else json_data.get("claimant_age"),
            "claimant_gender": self.claimant_gender or json_data.get("claimant_gender"),
            "claimant_city": self.claimant_city or json_data.get("claimant_city"),
            "claimant_state": self.claimant_state or json_data.get("claimant_state"),
            "vehicle_make": self.vehicle_make or json_data.get("vehicle_make"),
            "vehicle_model": self.vehicle_model or json_data.get("vehicle_model"),
            "vehicle_year": self.vehicle_year if self.vehicle_year is not None else json_data.get("vehicle_year"),
            "vehicle_use_type": self.vehicle_use_type or json_data.get("vehicle_use_type"),
            "vehicle_mileage": self.vehicle_mileage if self.vehicle_mileage is not None else json_data.get("vehicle_mileage"),
            "damage_severity": self.damage_severity or json_data.get("damage_severity"),
            "injury_severity": self.injury_severity or json_data.get("injury_severity"),
            "medical_treatment_received": self.medical_treatment_received if self.medical_treatment_received is not None else json_data.get("medical_treatment_received"),
            "medical_cost_estimate": self.medical_cost_estimate if self.medical_cost_estimate is not None else json_data.get("medical_cost_estimate"),
            "airbags_deployed": self.airbags_deployed if self.airbags_deployed is not None else json_data.get("airbags_deployed"),
            "policy_tenure_months": self.policy_tenure_months if self.policy_tenure_months is not None else json_data.get("policy_tenure_months"),
            "coverage_type": self.coverage_type or json_data.get("coverage_type"),
            "policy_type": self.policy_type or json_data.get("policy_type"),
            "deductible_amount": self.deductible_amount if self.deductible_amount is not None else json_data.get("deductible_amount"),
            "previous_claims_count": self.previous_claims_count if self.previous_claims_count is not None else json_data.get("previous_claims_count"),
            "lawyer_name": self.lawyer_name or json_data.get("lawyer_name"),
            "medical_provider_name": self.medical_provider_name or json_data.get("medical_provider_name"),
            "repair_shop_name": self.repair_shop_name or json_data.get("repair_shop_name"),
            "reported_by": self.reported_by or json_data.get("reported_by"),
            "photos": self.photos_url or json_data.get("photos"),
            "photos_url": self.photos_url or json_data.get("photos_url"),
            "status": self.status or json_data.get("status"),
            "fraud_label": self.fraud_label if self.fraud_label is not None else json_data.get("fraud_label"),
            
            # Legacy fields
            "doctor": self.doctor or json_data.get("doctor"),
            "lawyer": self.lawyer or json_data.get("lawyer"),
            "ip_address": self.ip_address or json_data.get("ip_address"),
            "accident_type": self.accident_type or json_data.get("accident_type"),
            "description": self.accident_description or json_data.get("description"),
            "claim_date": format_datetime(self.claim_date) or json_data.get("claim_date"),
            
            # Risk scoring fields
            "risk_score": self.risk_score or 0,
            "risk_category": self.risk_category or "low",
            "fraud_nlp_score": self.fraud_nlp_score if self.fraud_nlp_score is not None else json_data.get("fraud_nlp_score", 0),
            
            # Metadata
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
            "summary": self.summary or json_data.get("summary"),
            "missing_docs": self.missing_docs if self.missing_docs else json_data.get("missing_docs", []),
            
            # Compatibility fields for frontend
            "claimantName": self.claimant_name or json_data.get("claimant_name") or "Unknown",
            "policyNumber": self.policy_number or json_data.get("policy_number") or "N/A",
            "incidentDate": format_datetime(self.accident_date) or json_data.get("accident_date") or format_datetime(self.claim_date),
            "incidentType": self.loss_type or self.accident_type or json_data.get("loss_type") or json_data.get("accident_type") or "Unknown",
            "riskScore": self.risk_score or 0,
            "missingDocs": self.missing_docs if self.missing_docs else json_data.get("missing_docs", []),
        }
        
        # Remove None values to keep response clean (but keep 0, False, empty strings)
        cleaned_result = {}
        for key, value in result.items():
            if value is not None:
                cleaned_result[key] = value
        
        return cleaned_result


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

