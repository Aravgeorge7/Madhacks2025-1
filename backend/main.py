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
from model_service import get_model_service
from ai_service import analyze_claim_text

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

# Initialize model service (singleton)
model_service = get_model_service()


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
            // Pre-fill form if data is provided in URL
            function prefillForm() {
                const urlParams = new URLSearchParams(window.location.search);
                const prefillData = urlParams.get('prefill');
                
                if (prefillData) {
                    try {
                        const data = JSON.parse(decodeURIComponent(prefillData));
                        console.log('Pre-filling form with:', data);
                        
                        // Map data fields to form fields - handle both camelCase and snake_case
                        const setValue = (fieldName, value) => {
                            const field = document.getElementById(fieldName) || document.querySelector(`[name="${fieldName}"]`);
                            if (field && value !== undefined && value !== null && value !== '') {
                                // Handle dates - strip time portion
                                if (fieldName.includes('date') && typeof value === 'string') {
                                    field.value = value.split('T')[0];
                                } else {
                                    field.value = value;
                                }
                            }
                        };
                        
                        // Fill in all possible fields
                        setValue('claimant_name', data.claimantName || data.claimant_name);
                        setValue('policy_number', data.policyNumber || data.policy_number);
                        setValue('claim_submission_date', data.claim_submission_date);
                        setValue('accident_date', data.accident_date || data.incidentDate);
                        setValue('accident_time', data.accident_time);
                        setValue('accident_location_city', data.accident_location_city || data.claimant_city);
                        setValue('accident_location_state', data.accident_location_state || data.claimant_state);
                        setValue('accident_description', data.accident_description || data.description);
                        setValue('police_report_filed', data.police_report_filed);
                        setValue('loss_type', data.loss_type || data.incidentType);
                        setValue('claimant_age', data.claimant_age);
                        setValue('claimant_gender', data.claimant_gender);
                        setValue('claimant_city', data.claimant_city);
                        setValue('claimant_state', data.claimant_state);
                        setValue('vehicle_make', data.vehicle_make);
                        setValue('vehicle_model', data.vehicle_model);
                        setValue('vehicle_year', data.vehicle_year);
                        setValue('vehicle_use_type', data.vehicle_use_type);
                        setValue('vehicle_mileage', data.vehicle_mileage);
                        setValue('damage_severity', data.damage_severity);
                        setValue('injury_severity', data.injury_severity);
                        setValue('medical_treatment_received', data.medical_treatment_received);
                        setValue('medical_cost_estimate', data.medical_cost_estimate);
                        setValue('airbags_deployed', data.airbags_deployed);
                        setValue('policy_tenure_months', data.policy_tenure_months);
                        setValue('coverage_type', data.coverage_type);
                        setValue('policy_type', data.policy_type);
                        setValue('deductible_amount', data.deductible_amount);
                        setValue('previous_claims_count', data.previous_claims_count);
                        setValue('lawyer_name', data.lawyer_name);
                        setValue('medical_provider_name', data.medical_provider_name);
                        setValue('repair_shop_name', data.repair_shop_name);
                        setValue('reported_by', data.reported_by);
                        setValue('ip_address', data.ip_address);
                        
                        // Make form read-only
                        const form = document.getElementById('claimForm');
                        if (form) {
                            // Disable all input fields
                            const inputs = form.querySelectorAll('input, select, textarea');
                            inputs.forEach(input => {
                                input.setAttribute('readonly', true);
                                input.setAttribute('disabled', true);
                                input.style.backgroundColor = '#f5f5f5';
                                input.style.cursor = 'not-allowed';
                            });
                            
                            // Hide submit button
                            const submitBtn = form.querySelector('button[type="submit"]');
                            if (submitBtn) {
                                submitBtn.style.display = 'none';
                            }
                            
                            // Add read-only notice
                            const submitSection = form.querySelector('.submit-section');
                            if (submitSection) {
                                submitSection.innerHTML = '<p style="text-align: center; color: #666; font-size: 14px; padding: 20px; background: #f8f9fa; border-radius: 4px;"><strong>Read-Only View</strong><br>This claim has already been submitted and cannot be modified.</p>';
                            }
                        }
                        
                        // Update header to indicate viewing mode
                        const header = document.querySelector('.header h1');
                        if (header) {
                            header.textContent = 'View Submitted Claim';
                            header.style.background = 'linear-gradient(135deg, #2d5016 0%, #4a7c2e 100%)';
                        }
                        const subtitle = document.querySelector('.header .subtitle');
                        if (subtitle) {
                            subtitle.textContent = 'Read-Only - Claim Already Submitted';
                        }
                        
                    } catch (error) {
                        console.error('Error pre-filling form:', error);
                    }
                }
            }
            
            // Call prefill when page loads
            window.addEventListener('DOMContentLoaded', prefillForm);
            
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
        
        # Calculate previous claims count automatically if not provided
        # Query database for claims by same claimant_name or policy_number
        previous_claims_count = claim_data.previous_claims_count
        if previous_claims_count is None or previous_claims_count == 0:
            # Count existing claims by same claimant name or policy number
            claimant_name = claim_data.claimant_name
            policy_number = claim_data.policy_number
            
            count_query = db.query(Claim)
            if claimant_name:
                count_query = count_query.filter(Claim.claimant_name == claimant_name)
            elif policy_number:
                count_query = count_query.filter(Claim.policy_number == policy_number)
            else:
                count_query = None
            
            if count_query:
                previous_claims_count = count_query.count()
            else:
                previous_claims_count = 0
        
        # Convert form data to JSON and update with calculated previous_claims_count
        claim_json = claim_data.model_dump()
        claim_json["previous_claims_count"] = previous_claims_count
        
        # AI Analysis: Use GPT-4o-mini for consistency checking and fraud detection
        # This analyzes the description against metadata and detects inconsistencies
        ai_analysis = analyze_claim_text(claim_data)
        fraud_nlp_score = ai_analysis.get("fraud_nlp_score", 0)
        consistency_flags = ai_analysis.get("consistency_flags", [])
        analysis_summary = ai_analysis.get("analysis_summary", "")
        
        # Log AI analysis results
        if consistency_flags:
            print(f"🔍 AI Consistency Check: Found {len(consistency_flags)} inconsistency flags")
            for flag in consistency_flags:
                print(f"   ⚠️  {flag}")
        if analysis_summary:
            print(f"📊 AI Analysis Summary: {analysis_summary}")
        print(f"🎯 AI Fraud NLP Score: {fraud_nlp_score}/20")

        # Prepare data for graph processing (use new field names)
        # Generate unique IP if not provided to avoid false fraud ring detection
        import hashlib
        unique_ip = claim_data.ip_address
        if not unique_ip:
            # Generate a unique IP based on claim_id to avoid false positives
            ip_hash = hashlib.md5(claim_id.encode()).hexdigest()[:8]
            unique_ip = f"10.{int(ip_hash[:2], 16) % 256}.{int(ip_hash[2:4], 16) % 256}.{int(ip_hash[4:6], 16) % 256}"

        # Get accident description for graph processing
        accident_description = (
            claim_data.accident_description or 
            claim_data.description or 
            ""
        )

        graph_claim_data = {
            "claim_id": claim_id,
            "claimant_name": claim_data.claimant_name or f"{claim_data.claimant_city or 'Unknown'} Claimant",
            "doctor": claim_data.medical_provider_name or claim_data.doctor or "None",
            "lawyer": claim_data.lawyer_name or claim_data.lawyer or "None",
            "ip_address": unique_ip,
            "missing_docs": [] if claim_data.police_report_filed else ['police_report'],
            "fraud_nlp_score": fraud_nlp_score,  # Set based on AI analysis
            "accident_description": accident_description,  # Pass description for graph processing
            "description": accident_description  # Also pass as description for compatibility
        }
        
        # Calculate previous claims count automatically if not provided
        # Query database for claims by same claimant_name or policy_number
        previous_claims_count = claim_data.previous_claims_count
        if previous_claims_count is None or previous_claims_count == 0:
            # Count existing claims by same claimant name or policy number
            claimant_name = claim_data.claimant_name
            policy_number = claim_data.policy_number
            
            count_query = db.query(Claim)
            if claimant_name:
                count_query = count_query.filter(Claim.claimant_name == claimant_name)
            elif policy_number:
                count_query = count_query.filter(Claim.policy_number == policy_number)
            else:
                count_query = None
            
            if count_query:
                previous_claims_count = count_query.count()
            else:
                previous_claims_count = 0
        
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
            previous_claims_count=previous_claims_count,
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
            ip_address=unique_ip,  # Use the unique IP generated above
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


@app.get("/api/claims/{claim_id}")
async def get_claim_by_id(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """Get a single claim by its database ID."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.to_dict()


@app.get("/api/claims")
async def get_claims(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    include_model_scores: bool = True,
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
            (Claim.status == "unsettled") | 
            (Claim.status == "pending") |
            (Claim.status == None)
        )
    
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to dicts
    claim_dicts = [claim.to_dict() for claim in claims]
    
    # Add model scores if requested
    if include_model_scores and claims:
        try:
            # Get all claims for graph building
            all_claims_query = db.query(Claim).filter(
                (Claim.status == "unsettled") | 
                (Claim.status == "pending") |
                (Claim.status == None)
            )
            all_claims = all_claims_query.all()
            
            # Build graph from all claims
            all_claims_data = []
            for c in all_claims:
                claim_data = {
                    "claim_id": c.claim_id,
                    "claimant_name": c.claimant_name,
                    "lawyer_name": c.lawyer_name,
                    "medical_provider_name": c.medical_provider_name,
                    "ip_address": c.ip_address,
                    "accident_date": c.accident_date,
                    "claim_submission_date": c.claim_submission_date,
                    "accident_location_state": c.accident_location_state,
                    "police_report_filed": c.police_report_filed,
                    "previous_claims_count": c.previous_claims_count,
                    "accident_time": c.accident_time,
                    "accident_location_city": c.accident_location_city,
                    "accident_description": c.accident_description,
                    "loss_type": c.loss_type,
                    "claimant_age": c.claimant_age,
                    "claimant_gender": c.claimant_gender,
                    "claimant_city": c.claimant_city,
                    "claimant_state": c.claimant_state,
                    "vehicle_make": c.vehicle_make,
                    "vehicle_model": c.vehicle_model,
                    "vehicle_year": c.vehicle_year,
                    "vehicle_use_type": c.vehicle_use_type,
                    "vehicle_mileage": c.vehicle_mileage,
                    "damage_severity": c.damage_severity,
                    "injury_severity": c.injury_severity,
                    "medical_treatment_received": c.medical_treatment_received,
                    "medical_cost_estimate": c.medical_cost_estimate,
                    "airbags_deployed": c.airbags_deployed,
                    "policy_tenure_months": c.policy_tenure_months,
                    "coverage_type": c.coverage_type,
                    "policy_type": c.policy_type,
                    "deductible_amount": c.deductible_amount,
                    "repair_shop_name": c.repair_shop_name,
                    "reported_by": c.reported_by,
                }
                all_claims_data.append(claim_data)
            
            # Build graph once
            model_service.build_graph_from_claims(all_claims_data)
            
            # Score each claim
            for i, claim in enumerate(claims):
                claim_data = {
                    "claim_id": claim.claim_id,
                    "claimant_name": claim.claimant_name,
                    "lawyer_name": claim.lawyer_name,
                    "medical_provider_name": claim.medical_provider_name,
                    "ip_address": claim.ip_address,
                    "accident_date": claim.accident_date,
                    "claim_submission_date": claim.claim_submission_date,
                    "accident_location_state": claim.accident_location_state,
                    "police_report_filed": claim.police_report_filed,
                    "previous_claims_count": claim.previous_claims_count,
                    "accident_time": claim.accident_time,
                    "accident_location_city": claim.accident_location_city,
                    "accident_description": claim.accident_description,
                    "loss_type": claim.loss_type,
                    "claimant_age": claim.claimant_age,
                    "claimant_gender": claim.claimant_gender,
                    "claimant_city": claim.claimant_city,
                    "claimant_state": claim.claimant_state,
                    "vehicle_make": claim.vehicle_make,
                    "vehicle_model": claim.vehicle_model,
                    "vehicle_year": claim.vehicle_year,
                    "vehicle_use_type": claim.vehicle_use_type,
                    "vehicle_mileage": claim.vehicle_mileage,
                    "damage_severity": claim.damage_severity,
                    "injury_severity": claim.injury_severity,
                    "medical_treatment_received": claim.medical_treatment_received,
                    "medical_cost_estimate": claim.medical_cost_estimate,
                    "airbags_deployed": claim.airbags_deployed,
                    "policy_tenure_months": claim.policy_tenure_months,
                    "coverage_type": claim.coverage_type,
                    "policy_type": claim.policy_type,
                    "deductible_amount": claim.deductible_amount,
                    "repair_shop_name": claim.repair_shop_name,
                    "reported_by": claim.reported_by,
                }
                
                score_result = model_service.score_claim(claim_data, all_claims_data)
                claim_dicts[i]["modelRiskScore"] = score_result["risk_score"]
                claim_dicts[i]["modelRiskCategory"] = score_result["risk_category"]
                claim_dicts[i]["riskBreakdown"] = score_result["breakdown"]
                claim_dicts[i]["graphFeatures"] = score_result["features"]
                claim_dicts[i]["modelDetails"] = {
                    "model_score": score_result["model_score"],
                    "graph_risk": score_result["graph_risk"],
                    "rule_adjustment": score_result["rule_adjustment"]
                }
        except Exception as e:
            print(f"Error computing model scores: {e}")
            import traceback
            traceback.print_exc()
    
    return claim_dicts


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Get a specific claim by ID."""
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.to_dict()


@app.get("/api/graph")
async def get_graph_data(db: Session = Depends(get_db)):
    """
    Get graph data for 3D visualization showing connections between claims.
    Returns nodes (claims, doctors, lawyers, IPs) and edges (connections).
    """
    # Get all claims from database
    all_claims = db.query(Claim).all()
    
    # Build graph from all claims
    graph_data = {
        "nodes": [],
        "edges": []
    }
    
    # Track entities to avoid duplicates
    nodes_map = {}  # node_id -> node_data
    edges_set = set()  # (source, target, type) tuples
    
    node_id_counter = 0
    
    for claim in all_claims:
        claim_id = claim.claim_id
        claim_node_id = f"claim_{claim_id}"
        
        # Add claim node
        if claim_node_id not in nodes_map:
            nodes_map[claim_node_id] = {
                "id": claim_node_id,
                "type": "claim",
                "label": claim_id,
                "claimant_name": claim.claimant_name or "Unknown",
                "risk_score": claim.risk_score or 0,
                "risk_category": claim.risk_category or "low",
                "status": claim.status or "unknown"
            }
        
        # Add connections based on shared entities
        entities = {
            "doctor": claim.medical_provider_name or claim.doctor,
            "lawyer": claim.lawyer_name or claim.lawyer,
            "ip": claim.ip_address,
            "person": claim.claimant_name
        }
        
        for entity_type, entity_value in entities.items():
            if entity_value and str(entity_value).strip() and str(entity_value).lower() != "none":
                entity_node_id = f"{entity_type}_{entity_value}"
                
                # Add entity node
                if entity_node_id not in nodes_map:
                    nodes_map[entity_node_id] = {
                        "id": entity_node_id,
                        "type": entity_type,
                        "label": str(entity_value)[:30],  # Truncate long names
                        "entity_value": str(entity_value)
                    }
                
                # Add edge from claim to entity
                edge_key = (claim_node_id, entity_node_id, entity_type)
                if edge_key not in edges_set:
                    edges_set.add(edge_key)
    
    # Find connections between claims (shared entities)
    # Group entities by their connected claims
    entity_to_claims = {}
    for edge_key in edges_set:
        source, target, edge_type = edge_key
        if source.startswith("claim_") and not target.startswith("claim_"):
            if target not in entity_to_claims:
                entity_to_claims[target] = []
            entity_to_claims[target].append(source)
    
    # Add edges between claims that share entities
    for entity_id, connected_claims in entity_to_claims.items():
        if len(connected_claims) > 1:
            # Connect all claims that share this entity
            for i, claim1 in enumerate(connected_claims):
                for claim2 in connected_claims[i+1:]:
                    connection_type = nodes_map[entity_id]["type"]
                    edge_key = (claim1, claim2, f"shared_{connection_type}")
                    if edge_key not in edges_set:
                        edges_set.add(edge_key)
    
    # Convert to lists
    graph_data["nodes"] = list(nodes_map.values())
    graph_data["edges"] = [
        {
            "id": f"edge_{i}",
            "source": source,
            "target": target,
            "type": edge_type,
            "relationship": edge_type
        }
        for i, (source, target, edge_type) in enumerate(edges_set)
    ]
    
    return graph_data


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
@app.get("/api/graph/{claim_id}")
async def get_claim_graph(claim_id: str):
    """Get the network graph (subgraph) for a specific claim."""
    # Get 2 hops of connections (Claim -> Doctor -> Other Claims)
    return risk_graph.get_claim_subgraph(claim_id, hops=2)

