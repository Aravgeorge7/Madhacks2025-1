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
    status = Column(String, default="pending")
    
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
        """Convert claim to dictionary."""
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "claimant_name": self.claimant_name,
            "doctor": self.doctor,
            "lawyer": self.lawyer,
            "ip_address": self.ip_address,
            "accident_type": self.accident_type,
            "claim_date": self.claim_date.isoformat() if self.claim_date else None,
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "fraud_nlp_score": self.fraud_nlp_score,
            "claim_data_json": self.claim_data_json,
            "summary": self.summary,
            "missing_docs": self.missing_docs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


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

