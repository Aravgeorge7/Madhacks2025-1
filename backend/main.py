"""
FastAPI application for RiskChain Intelligence
"""

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime

from database import init_db, get_db, Claim
from models import ClaimFormData, ClaimResponse
from graph_service import RiskGraph

# Initialize FastAPI app
app = FastAPI(
    title="RiskChain Intelligence API",
    description="Insurance fraud detection using AI and graph analysis",
    version="1.0.0"
)

# CORS middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize graph service (singleton)
risk_graph = RiskGraph()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("🚀 RiskChain Intelligence API started")
    print("📊 Database initialized")
    print("🔗 Graph service ready")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with form for testing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Insurance Claim Submission Form - RiskChain Intelligence</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Georgia', 'Times New Roman', serif;
                background-color: #f8f9fa;
                color: #2c3e50;
                line-height: 1.6;
                padding: 20px;
            }
            .form-wrapper {
                max-width: 900px;
                margin: 0 auto;
                background: #ffffff;
                border: 1px solid #dee2e6;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .header {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: #ffffff;
                padding: 40px 50px;
                border-bottom: 4px solid #1a2f5a;
            }
            .header h1 {
                font-size: 28px;
                font-weight: 600;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
                text-align: center;
            }
            .header .subtitle {
                font-size: 14px;
                text-align: center;
                opacity: 0.95;
                font-weight: 300;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            .form-container {
                padding: 50px;
            }
            .disclaimer {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px 20px;
                margin-bottom: 30px;
                font-size: 13px;
                color: #856404;
            }
            .disclaimer strong {
                display: block;
                margin-bottom: 5px;
                font-size: 14px;
            }
            .section {
                margin-bottom: 40px;
                border-bottom: 2px solid #e9ecef;
                padding-bottom: 30px;
            }
            .section:last-child {
                border-bottom: none;
            }
            .section-title {
                font-size: 20px;
                font-weight: 600;
                color: #1e3c72;
                margin-bottom: 25px;
                padding-bottom: 10px;
                border-bottom: 2px solid #1e3c72;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .form-group {
                margin-bottom: 25px;
            }
            .form-group label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #495057;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            .form-group label .required {
                color: #dc3545;
                font-weight: 700;
                margin-left: 3px;
            }
            .form-group input[type="text"],
            .form-group input[type="date"],
            .form-group input[type="number"],
            .form-group textarea,
            .form-group select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                font-family: 'Georgia', 'Times New Roman', serif;
                background-color: #ffffff;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus,
            .form-group textarea:focus,
            .form-group select:focus {
                outline: none;
                border-color: #1e3c72;
                box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
            }
            .form-group textarea {
                min-height: 120px;
                resize: vertical;
                line-height: 1.8;
            }
            .form-group small {
                display: block;
                margin-top: 6px;
                font-size: 12px;
                color: #6c757d;
                font-style: italic;
            }
            .checkbox-group {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-top: 10px;
            }
            .checkbox-item {
                display: flex;
                align-items: center;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            .checkbox-item input[type="checkbox"] {
                margin-right: 10px;
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            .checkbox-item label {
                font-weight: 400;
                text-transform: none;
                margin: 0;
                cursor: pointer;
                color: #495057;
            }
            .submit-section {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #e9ecef;
                text-align: center;
            }
            .submit-button {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: #ffffff;
                padding: 16px 50px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .submit-button:hover {
                background: linear-gradient(135deg, #1a2f5a 0%, #1e3c72 100%);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
            }
            .submit-button:active {
                transform: translateY(0);
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                border-radius: 4px;
                display: none;
                border: 2px solid;
            }
            .result.success {
                background-color: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            .result.error {
                background-color: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            .result h3 {
                margin-bottom: 10px;
                font-size: 18px;
            }
            .footer {
                background-color: #f8f9fa;
                padding: 20px 50px;
                text-align: center;
                font-size: 12px;
                color: #6c757d;
                border-top: 1px solid #dee2e6;
            }
            @media (max-width: 768px) {
                .form-container {
                    padding: 30px 20px;
                }
                .header {
                    padding: 30px 20px;
                }
                .checkbox-group {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="form-wrapper">
            <div class="header">
                <h1>INSURANCE CLAIM SUBMISSION FORM</h1>
                <div class="subtitle">RiskChain Intelligence - Auto & Healthcare Claims Processing</div>
            </div>
            
            <div class="form-container">
                <div class="disclaimer">
                    <strong>IMPORTANT NOTICE:</strong>
                    Please complete all required fields marked with an asterisk (*). 
                    Incomplete submissions may result in processing delays. 
                    All information provided will be subject to verification and fraud detection analysis.
                </div>
                
                <form id="claimForm">
                    <div class="section">
                        <div class="section-title">I. Claim Identification</div>
                        <div class="form-group">
                            <label>Insurance Policy Number</label>
                            <input name="policy_number" type="text" placeholder="Enter policy number">
                            <small>Enter policy number</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">II. Dates and Times</div>
                        <div class="form-group">
                            <label>Claim Submission Date</label>
                            <input name="claim_submission_date" type="date">
                        </div>
                        <div class="form-group">
                            <label>Date of Accident</label>
                            <input name="accident_date" type="date">
                        </div>
                        <div class="form-group">
                            <label>Time of Accident</label>
                            <input name="accident_time" type="time" placeholder="HH:MM format">
                            <small>HH:MM format</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">III. Location Information</div>
                        <div class="form-group">
                            <label>Accident Location - City</label>
                            <input name="accident_location_city" type="text" placeholder="City where accident occurred">
                            <small>City where accident occurred</small>
                        </div>
                        <div class="form-group">
                            <label>Accident Location - State</label>
                            <input name="accident_location_state" type="text" placeholder="State where accident occurred (e.g., CA, NY)">
                            <small>State where accident occurred (e.g., CA, NY)</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">IV. Claimant Information</div>
                        <div class="form-group">
                            <label>Claimant Name</label>
                            <input name="claimant_name" type="text" placeholder="Full name of the claimant" required>
                            <small>Full name of the claimant</small>
                        </div>
                        <div class="form-group">
                            <label>Claimant Age</label>
                            <input name="claimant_age" type="number" placeholder="Enter age" step="1">
                            <small>Enter age</small>
                        </div>
                        <div class="form-group">
                            <label>Claimant Gender</label>
                            <select name="claimant_gender">
                                <option value="">-- Please Select --</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Claimant City</label>
                            <input name="claimant_city" type="text" placeholder="City of residence">
                            <small>City of residence</small>
                        </div>
                        <div class="form-group">
                            <label>Claimant State</label>
                            <input name="claimant_state" type="text" placeholder="State of residence">
                            <small>State of residence</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">V. Vehicle Information</div>
                        <div class="form-group">
                            <label>Vehicle Make</label>
                            <input name="vehicle_make" type="text" placeholder="e.g., Toyota, Honda, Ford">
                            <small>e.g., Toyota, Honda, Ford</small>
                        </div>
                        <div class="form-group">
                            <label>Vehicle Model</label>
                            <input name="vehicle_model" type="text" placeholder="e.g., Camry, Accord, F-150">
                            <small>e.g., Camry, Accord, F-150</small>
                        </div>
                        <div class="form-group">
                            <label>Vehicle Year</label>
                            <input name="vehicle_year" type="number" placeholder="e.g., 2020" step="1">
                            <small>e.g., 2020</small>
                        </div>
                        <div class="form-group">
                            <label>Vehicle Use Type</label>
                            <select name="vehicle_use_type">
                                <option value="">-- Please Select --</option>
                                <option value="personal">Personal</option>
                                <option value="commercial">Commercial</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Vehicle Mileage</label>
                            <input name="vehicle_mileage" type="number" placeholder="Current odometer reading" step="1">
                            <small>Current odometer reading</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">VI. Incident Details</div>
                        <div class="form-group">
                            <label>Loss Type</label>
                            <select name="loss_type">
                                <option value="">-- Please Select --</option>
                                <option value="collision">Collision</option>
                                <option value="comprehensive">Comprehensive</option>
                                <option value="liability">Liability</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Accident Description</label>
                            <textarea name="accident_description" rows="4" placeholder="Provide detailed description of the accident"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Police Report Filed</label>
                            <select name="police_report_filed">
                                <option value="">-- Please Select --</option>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">VII. Damage and Injury Information</div>
                        <div class="form-group">
                            <label>Damage Severity</label>
                            <select name="damage_severity">
                                <option value="">-- Please Select --</option>
                                <option value="minor">Minor</option>
                                <option value="moderate">Moderate</option>
                                <option value="major">Major</option>
                                <option value="total_loss">Total Loss</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Injury Severity</label>
                            <select name="injury_severity">
                                <option value="">-- Please Select --</option>
                                <option value="none">None</option>
                                <option value="minor">Minor</option>
                                <option value="moderate">Moderate</option>
                                <option value="severe">Severe</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Medical Treatment Received</label>
                            <select name="medical_treatment_received">
                                <option value="">-- Please Select --</option>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Medical Cost Estimate ($)</label>
                            <input name="medical_cost_estimate" type="number" placeholder="Estimated medical costs" step="0.01">
                            <small>Estimated medical costs</small>
                        </div>
                        <div class="form-group">
                            <label>Airbags Deployed</label>
                            <select name="airbags_deployed">
                                <option value="">-- Please Select --</option>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">VIII. Policy Information</div>
                        <div class="form-group">
                            <label>Policy Tenure (Months)</label>
                            <input name="policy_tenure_months" type="number" placeholder="Number of months policy has been active" step="1">
                            <small>Number of months policy has been active</small>
                        </div>
                        <div class="form-group">
                            <label>Coverage Type</label>
                            <select name="coverage_type">
                                <option value="">-- Please Select --</option>
                                <option value="collision">Collision</option>
                                <option value="comprehensive">Comprehensive</option>
                                <option value="liability_only">Liability Only</option>
                                <option value="full_coverage">Full Coverage</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Policy Type</label>
                            <select name="policy_type">
                                <option value="">-- Please Select --</option>
                                <option value="collision_only">Collision Only</option>
                                <option value="comprehensive_only">Comprehensive Only</option>
                                <option value="liability_only">Liability Only</option>
                                <option value="full">Full</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Deductible Amount ($)</label>
                            <input name="deductible_amount" type="number" placeholder="Deductible amount" step="0.01">
                            <small>Deductible amount</small>
                        </div>
                        <div class="form-group">
                            <label>Previous Claims Count</label>
                            <input name="previous_claims_count" type="number" placeholder="Number of previous claims" step="1">
                            <small>Number of previous claims</small>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">IX. Service Providers</div>
                        <div class="form-group">
                            <label>Lawyer/Attorney Name</label>
                            <input name="lawyer_name" type="text" placeholder="Name of legal representative">
                            <small>Name of legal representative</small>
                        </div>
                        <div class="form-group">
                            <label>Medical Provider Name</label>
                            <input name="medical_provider_name" type="text" placeholder="Name of medical provider/facility">
                            <small>Name of medical provider/facility</small>
                        </div>
                        <div class="form-group">
                            <label>Repair Shop Name</label>
                            <input name="repair_shop_name" type="text" placeholder="Name of repair shop">
                            <small>Name of repair shop</small>
                        </div>
                        <div class="form-group">
                            <label>Reported By</label>
                            <select name="reported_by">
                                <option value="">-- Please Select --</option>
                                <option value="self">Self</option>
                                <option value="agent">Agent</option>
                                <option value="third_party">Third Party</option>
                            </select>
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">X. Additional Information</div>
                        <div class="form-group">
                            <label>Photo URL</label>
                            <input name="photos" type="text" placeholder="URL to accident photos">
                            <small>URL to accident photos</small>
                        </div>
                        <div class="form-group">
                            <label>IP Address</label>
                            <input name="ip_address" type="text" placeholder="IP address (auto-detected if left blank)">
                            <small>IP address (auto-detected if left blank)</small>
                        </div>
                    </div>
                    
                    <div class="submit-section">
                        <button type="submit" class="submit-button">Submit Claim for Processing</button>
                    </div>
                </form>
            
                <div id="result" class="result"></div>
            </div>
            
            <div class="footer">
                <p><strong>RiskChain Intelligence</strong> | Insurance Fraud Detection & Risk Analysis System</p>
                <p>All claims are subject to automated fraud detection and risk assessment</p>
                <p style="margin-top: 10px; font-size: 11px;">© 2024 RiskChain Intelligence. All rights reserved.</p>
            </div>
        </div>
        
        <script>
            document.getElementById('claimForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                
                // Collect form data
                for (let [key, value] of formData.entries()) {
                    if (key === 'missing_docs') {
                        if (!data[key]) data[key] = [];
                        data[key].push(value);
                    } else {
                        data[key] = value || null;
                    }
                }
                
                // Remove empty missing_docs if no checkboxes selected
                if (data.missing_docs && data.missing_docs.length === 0) {
                    data.missing_docs = [];
                }
                
                try {
                    const response = await fetch('/api/claims', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    const resultDiv = document.getElementById('result');
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>CLAIM SUBMITTED SUCCESSFULLY</h3>
                            <p><strong>Claim Reference Number:</strong> ${result.claim_id}</p>
                            <p><strong>Risk Assessment Score:</strong> ${result.risk_score}/100 (${result.risk_category.toUpperCase()})</p>
                            <p><strong>Submission Timestamp:</strong> ${new Date(result.created_at).toLocaleString()}</p>
                            <p style="margin-top: 15px; font-size: 13px;">Your claim has been received and is being processed. You will receive confirmation via email.</p>
                        `;
                        resultDiv.style.display = 'block';
                        this.reset();
                        
                        // Notify parent window (dashboard) that a claim was submitted
                        if (window.parent && window.parent !== window) {
                            try {
                                window.parent.postMessage({
                                    type: 'CLAIM_SUBMITTED',
                                    claimId: result.claim_id,
                                    riskScore: result.risk_score
                                }, '*');
                            } catch (e) {
                                console.log('Could not notify parent window');
                            }
                        }
                        
                        // Also use localStorage for cross-tab communication
                        try {
                            localStorage.setItem('claimSubmitted', Date.now().toString());
                        } catch (e) {
                            console.log('Could not set localStorage');
                        }
                    } else {
                        throw new Error(result.detail || 'Submission failed');
                    }
                } catch (error) {
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<h3>SUBMISSION ERROR</h3><p>${error.message}</p><p style="margin-top: 10px; font-size: 13px;">Please review your information and try again. If the problem persists, contact support.</p>`;
                    resultDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/api/claims", response_model=ClaimResponse)
async def create_claim(
    claim_data: ClaimFormData,
    db: Session = Depends(get_db)
):
    """
    Create a new claim from form data.
    
    Converts form data to JSON and stores in database.
    Also processes the claim through the graph service to calculate risk score.
    """
    try:
        # Generate unique claim ID if not provided
        claim_id = claim_data.claim_id or f"C{str(uuid.uuid4())[:8].upper()}"
        
        # Convert form data to JSON
        claim_json = claim_data.model_dump()
        
        # Prepare data for graph processing (use new field names)
        graph_claim_data = {
            "claim_id": claim_id,
            "claimant_name": claim_data.claimant_name or f"{claim_data.claimant_city or 'Unknown'} Claimant",
            "doctor": claim_data.medical_provider_name or claim_data.doctor or "None",
            "lawyer": claim_data.lawyer_name or claim_data.lawyer or "None",
            "ip_address": claim_data.ip_address or "192.168.1.100",  # Default if not provided
            "missing_docs": [] if claim_data.police_report_filed else ['police_report'],
            "fraud_nlp_score": 0  # Will be updated when AI processing is added
        }
        
        # Process claim through graph service
        graph_result = risk_graph.process_claim(graph_claim_data)
        
        # Parse dates
        claim_submission_date = None
        if claim_data.claim_submission_date:
            try:
                claim_submission_date = datetime.fromisoformat(claim_data.claim_submission_date)
            except:
                claim_submission_date = datetime.utcnow()
        
        accident_date = None
        if claim_data.accident_date:
            try:
                accident_date = datetime.fromisoformat(claim_data.accident_date)
            except:
                pass
        
        # Create database record with all CSV fields
        db_claim = Claim(
            claim_id=claim_id,
            policy_number=claim_data.policy_number,
            claim_submission_date=claim_submission_date or datetime.utcnow(),
            accident_date=accident_date,
            accident_time=claim_data.accident_time,
            accident_location_city=claim_data.accident_location_city,
            accident_location_state=claim_data.accident_location_state,
            accident_description=claim_data.accident_description,
            police_report_filed=claim_data.police_report_filed or 0,
            loss_type=claim_data.loss_type,
            claimant_age=claim_data.claimant_age,
            claimant_gender=claim_data.claimant_gender,
            claimant_city=claim_data.claimant_city,
            claimant_state=claim_data.claimant_state,
            vehicle_make=claim_data.vehicle_make,
            vehicle_model=claim_data.vehicle_model,
            vehicle_year=claim_data.vehicle_year,
            vehicle_use_type=claim_data.vehicle_use_type,
            vehicle_mileage=claim_data.vehicle_mileage,
            damage_severity=claim_data.damage_severity,
            injury_severity=claim_data.injury_severity,
            medical_treatment_received=claim_data.medical_treatment_received or 0,
            medical_cost_estimate=claim_data.medical_cost_estimate,
            airbags_deployed=claim_data.airbags_deployed or 0,
            policy_tenure_months=claim_data.policy_tenure_months,
            coverage_type=claim_data.coverage_type,
            policy_type=claim_data.policy_type,
            deductible_amount=claim_data.deductible_amount,
            previous_claims_count=claim_data.previous_claims_count or 0,
            lawyer_name=claim_data.lawyer_name,
            medical_provider_name=claim_data.medical_provider_name,
            repair_shop_name=claim_data.repair_shop_name,
            reported_by=claim_data.reported_by,
            photos_url=claim_data.photos,
            status=claim_data.status or "unsettled",
            risk_score=graph_result["risk_score"],
            risk_category=graph_result["risk_category"],
            fraud_nlp_score=graph_result.get("fraud_nlp_score", 0),
            claim_data_json=claim_json,
            # Legacy fields for compatibility
            claimant_name=claim_data.claimant_name or f"{claim_data.claimant_city or 'Unknown'} Claimant",
            doctor=claim_data.medical_provider_name or claim_data.doctor,
            lawyer=claim_data.lawyer_name or claim_data.lawyer,
            ip_address=claim_data.ip_address or "192.168.1.100",
            accident_type=claim_data.loss_type or claim_data.accident_type,
            claim_date=accident_date or claim_submission_date or datetime.utcnow(),
            missing_docs=claim_data.missing_docs or []
        )
        
        db.add(db_claim)
        db.commit()
        db.refresh(db_claim)
        
        return ClaimResponse(
            id=db_claim.id,
            claim_id=db_claim.claim_id,
            policy_number=db_claim.policy_number,
            risk_score=db_claim.risk_score,
            risk_category=db_claim.risk_category,
            claim_data_json=db_claim.claim_data_json,
            created_at=db_claim.created_at.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating claim: {str(e)}")


@app.get("/api/claims")
async def get_claims(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get claims with pagination and optional status filter."""
    query = db.query(Claim)
    
    # Filter by status if provided
    if status:
        query = query.filter(Claim.status == status)
    else:
        # Default: get pending or unsettled claims
        query = query.filter(
            (Claim.status == "pending") | 
            (Claim.status == "unsettled") |
            (Claim.status == None)
        )
    
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return [claim.to_dict() for claim in claims]


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Get a specific claim by ID."""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.to_dict()


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get aggregated statistics."""
    total_claims = db.query(Claim).count()
    high_risk = db.query(Claim).filter(Claim.risk_category == "high").count()
    medium_risk = db.query(Claim).filter(Claim.risk_category == "medium").count()
    low_risk = db.query(Claim).filter(Claim.risk_category == "low").count()
    
    graph_stats = risk_graph.get_graph_stats()
    
    return {
        "total_claims": total_claims,
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "graph_stats": graph_stats
    }

