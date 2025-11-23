"""
Pydantic models for request/response validation
Updated to match CSV dataset structure
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClaimFormData(BaseModel):
    """Form data model for claim submission - matches CSV dataset structure."""
    
    # Claim Identification
    claim_id: Optional[str] = Field(None, description="Claim ID (auto-generated if not provided)")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")
    
    # Dates and Times
    claim_submission_date: Optional[str] = Field(None, description="Date claim was submitted")
    accident_date: Optional[str] = Field(None, description="Date of accident")
    accident_time: Optional[str] = Field(None, description="Time of accident")
    
    # Location Information
    accident_location_city: Optional[str] = Field(None, description="City where accident occurred")
    accident_location_state: Optional[str] = Field(None, description="State where accident occurred")
    
    # Incident Details
    accident_description: Optional[str] = Field(None, description="Detailed description of the accident")
    loss_type: Optional[str] = Field(None, description="Type of loss (collision, comprehensive, etc.)")
    police_report_filed: Optional[int] = Field(0, description="Whether police report was filed (0 or 1)")
    
    # Claimant Information
    claimant_age: Optional[int] = Field(None, description="Age of claimant")
    claimant_gender: Optional[str] = Field(None, description="Gender of claimant")
    claimant_city: Optional[str] = Field(None, description="City of claimant")
    claimant_state: Optional[str] = Field(None, description="State of claimant")
    
    # Vehicle Information
    vehicle_make: Optional[str] = Field(None, description="Vehicle manufacturer")
    vehicle_model: Optional[str] = Field(None, description="Vehicle model")
    vehicle_year: Optional[int] = Field(None, description="Vehicle year")
    vehicle_use_type: Optional[str] = Field(None, description="Vehicle use type (personal, commercial)")
    vehicle_mileage: Optional[int] = Field(None, description="Vehicle mileage")
    
    # Damage and Injury
    damage_severity: Optional[str] = Field(None, description="Severity of vehicle damage")
    injury_severity: Optional[str] = Field(None, description="Severity of injuries")
    medical_treatment_received: Optional[int] = Field(0, description="Whether medical treatment was received (0 or 1)")
    medical_cost_estimate: Optional[float] = Field(None, description="Estimated medical costs")
    airbags_deployed: Optional[int] = Field(0, description="Whether airbags deployed (0 or 1)")
    
    # Policy Information
    policy_tenure_months: Optional[int] = Field(None, description="Number of months policy has been active")
    coverage_type: Optional[str] = Field(None, description="Type of coverage")
    policy_type: Optional[str] = Field(None, description="Policy type")
    deductible_amount: Optional[float] = Field(None, description="Deductible amount")
    previous_claims_count: Optional[int] = Field(0, description="Number of previous claims")
    
    # Service Providers
    lawyer_name: Optional[str] = Field(None, description="Name of lawyer/attorney")
    medical_provider_name: Optional[str] = Field(None, description="Name of medical provider")
    repair_shop_name: Optional[str] = Field(None, description="Name of repair shop")
    reported_by: Optional[str] = Field(None, description="Who reported the claim")
    
    # Photos
    photos: Optional[str] = Field(None, description="URL to photos")
    
    # Status
    status: Optional[str] = Field("unsettled", description="Claim status")
    
    # Legacy fields (for backward compatibility)
    claimant_name: Optional[str] = Field(None, description="Name of claimant (legacy)")
    doctor: Optional[str] = Field(None, description="Doctor name (legacy - use medical_provider_name)")
    lawyer: Optional[str] = Field(None, description="Lawyer name (legacy - use lawyer_name)")
    ip_address: Optional[str] = Field(None, description="IP address from submission")
    accident_type: Optional[str] = Field(None, description="Type of accident (legacy - use loss_type)")
    description: Optional[str] = Field(None, description="Description (legacy - use accident_description)")
    claim_date: Optional[str] = Field(None, description="Claim date (legacy)")
    missing_docs: Optional[List[str]] = Field(default=[], description="List of missing documents")
    urgency: Optional[int] = Field(None, ge=1, le=5, description="Urgency level (1-5)")
    claim_amount: Optional[float] = Field(None, description="Claim amount")
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_number": "POL600000",
                "accident_date": "2024-06-29",
                "accident_time": "12:47:00",
                "accident_location_city": "Keithside",
                "accident_location_state": "ME",
                "accident_description": "Rear-end collision",
                "loss_type": "collision",
                "claimant_age": 35,
                "claimant_gender": "male",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2020
            }
        }


class ClaimResponse(BaseModel):
    """Response model for claim creation."""
    
    id: int
    claim_id: str
    policy_number: Optional[str]
    risk_score: int
    risk_category: str
    claim_data_json: dict
    created_at: str
    
    class Config:
        from_attributes = True
