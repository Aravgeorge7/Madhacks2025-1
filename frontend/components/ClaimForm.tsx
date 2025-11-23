"use client";

import { useState } from "react";

interface ClaimFormData {
  // Claim Identification
  policy_number?: string;
  
  // Dates and Times
  claim_submission_date?: string;
  accident_date?: string;
  accident_time?: string;
  
  // Location Information
  accident_location_city?: string;
  accident_location_state?: string;
  
  // Incident Details
  accident_description?: string;
  loss_type?: string;
  police_report_filed?: number;
  
  // Claimant Information
  claimant_name?: string;
  claimant_age?: number;
  claimant_gender?: string;
  claimant_city?: string;
  claimant_state?: string;
  
  // Vehicle Information
  vehicle_make?: string;
  vehicle_model?: string;
  vehicle_year?: number;
  vehicle_use_type?: string;
  vehicle_mileage?: number;
  
  // Damage and Injury
  damage_severity?: string;
  injury_severity?: string;
  medical_treatment_received?: number;
  medical_cost_estimate?: number;
  airbags_deployed?: number;
  
  // Policy Information
  policy_tenure_months?: number;
  coverage_type?: string;
  policy_type?: string;
  deductible_amount?: number;
  previous_claims_count?: number;
  
  // Service Providers
  lawyer_name?: string;
  lawyer?: string;
  medical_provider_name?: string;
  doctor?: string;
  repair_shop_name?: string;
  reported_by?: string;
  
  // Additional
  photos?: string;
  ip_address?: string;
  missing_docs?: string[];
  urgency?: number;
}

export default function ClaimForm() {
  const [formData, setFormData] = useState<ClaimFormData>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ success: boolean; message: string; claimId?: string } | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let processedValue: any = value;
    
    if (type === "number") {
      processedValue = value === "" ? undefined : Number(value);
    } else if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      processedValue = checked ? 1 : 0;
    }
    
    setFormData(prev => ({ ...prev, [name]: processedValue }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitResult(null);

    try {
      // Get client IP (simplified - in production, get from server)
      const ipAddress = formData.ip_address || "127.0.0.1";
      
      const payload = {
        ...formData,
        ip_address: ipAddress,
        doctor: formData.medical_provider_name || formData.doctor,
        lawyer: formData.lawyer_name || formData.lawyer,
        missing_docs: formData.missing_docs || [],
      };

      const response = await fetch("http://localhost:8000/api/claims", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to submit claim");
      }

      const result = await response.json();
      setSubmitResult({
        success: true,
        message: `Claim submitted successfully! Risk Score: ${result.risk_score}/100 (${result.risk_category})`,
        claimId: result.claim_id,
      });
      
      // Reset form
      setFormData({});
      
      // Refresh page after 3 seconds to show new claim
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    } catch (error: any) {
      setSubmitResult({
        success: false,
        message: error.message || "An error occurred while submitting the claim",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">Submit New Claim</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Claim Identification */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Claim Identification</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Policy Number</label>
              <input
                type="text"
                name="policy_number"
                value={formData.policy_number || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="POL600000"
              />
            </div>
          </div>
        </div>

        {/* Dates and Times */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Dates and Times</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Submission Date</label>
              <input
                type="date"
                name="claim_submission_date"
                value={formData.claim_submission_date || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accident Date</label>
              <input
                type="date"
                name="accident_date"
                value={formData.accident_date || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accident Time</label>
              <input
                type="time"
                name="accident_time"
                value={formData.accident_time || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
          </div>
        </div>

        {/* Location Information */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Location Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accident City</label>
              <input
                type="text"
                name="accident_location_city"
                value={formData.accident_location_city || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="City name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accident State</label>
              <input
                type="text"
                name="accident_location_state"
                value={formData.accident_location_state || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="State (e.g., CA, NY)"
                maxLength={2}
              />
            </div>
          </div>
        </div>

        {/* Claimant Information */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Claimant Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Claimant Name *</label>
              <input
                type="text"
                name="claimant_name"
                value={formData.claimant_name || ""}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Age</label>
              <input
                type="number"
                name="claimant_age"
                value={formData.claimant_age || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Age"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Gender</label>
              <select
                name="claimant_gender"
                value={formData.claimant_gender || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">City</label>
              <input
                type="text"
                name="claimant_city"
                value={formData.claimant_city || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="City of residence"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">State</label>
              <input
                type="text"
                name="claimant_state"
                value={formData.claimant_state || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="State"
                maxLength={2}
              />
            </div>
          </div>
        </div>

        {/* Vehicle Information */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Vehicle Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Make</label>
              <input
                type="text"
                name="vehicle_make"
                value={formData.vehicle_make || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Toyota, Honda, Ford"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Model</label>
              <input
                type="text"
                name="vehicle_model"
                value={formData.vehicle_model || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Camry, Accord, F-150"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Year</label>
              <input
                type="number"
                name="vehicle_year"
                value={formData.vehicle_year || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="2020"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Use Type</label>
              <select
                name="vehicle_use_type"
                value={formData.vehicle_use_type || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="personal">Personal</option>
                <option value="commercial">Commercial</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Mileage</label>
              <input
                type="number"
                name="vehicle_mileage"
                value={formData.vehicle_mileage || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Current odometer reading"
              />
            </div>
          </div>
        </div>

        {/* Incident Details */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Incident Details</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Loss Type</label>
              <select
                name="loss_type"
                value={formData.loss_type || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="collision">Collision</option>
                <option value="comprehensive">Comprehensive</option>
                <option value="liability">Liability</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accident Description</label>
              <textarea
                name="accident_description"
                value={formData.accident_description || ""}
                onChange={handleChange}
                rows={4}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Provide detailed description of the accident"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Police Report Filed</label>
              <select
                name="police_report_filed"
                value={formData.police_report_filed?.toString() || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
          </div>
        </div>

        {/* Damage and Injury */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Damage and Injury</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Damage Severity</label>
              <select
                name="damage_severity"
                value={formData.damage_severity || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="minor">Minor</option>
                <option value="moderate">Moderate</option>
                <option value="major">Major</option>
                <option value="total_loss">Total Loss</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Injury Severity</label>
              <select
                name="injury_severity"
                value={formData.injury_severity || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="none">None</option>
                <option value="minor">Minor</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Medical Treatment Received</label>
              <select
                name="medical_treatment_received"
                value={formData.medical_treatment_received?.toString() || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Medical Cost Estimate ($)</label>
              <input
                type="number"
                name="medical_cost_estimate"
                value={formData.medical_cost_estimate || ""}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Airbags Deployed</label>
              <select
                name="airbags_deployed"
                value={formData.airbags_deployed?.toString() || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
          </div>
        </div>

        {/* Service Providers */}
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-lg font-semibold text-slate-700 mb-4 uppercase tracking-wide">Service Providers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Lawyer/Attorney Name *</label>
              <input
                type="text"
                name="lawyer_name"
                value={formData.lawyer_name || ""}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Attorney name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Medical Provider Name *</label>
              <input
                type="text"
                name="medical_provider_name"
                value={formData.medical_provider_name || ""}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Doctor/Medical facility name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Repair Shop Name</label>
              <input
                type="text"
                name="repair_shop_name"
                value={formData.repair_shop_name || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
                placeholder="Repair shop name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Reported By</label>
              <select
                name="reported_by"
                value={formData.reported_by || ""}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select...</option>
                <option value="self">Self</option>
                <option value="agent">Agent</option>
                <option value="third_party">Third Party</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4 pt-4">
          <button
            type="button"
            onClick={() => setFormData({})}
            className="px-6 py-2 border border-slate-300 rounded-md text-slate-700 hover:bg-slate-50 transition-colors"
          >
            Clear Form
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Submitting..." : "Submit Claim"}
          </button>
        </div>

        {/* Result Message */}
        {submitResult && (
          <div
            className={`mt-4 p-4 rounded-md ${
              submitResult.success
                ? "bg-emerald-50 border border-emerald-200 text-emerald-800"
                : "bg-red-50 border border-red-200 text-red-800"
            }`}
          >
            <p className="font-medium">{submitResult.message}</p>
            {submitResult.claimId && (
              <p className="text-sm mt-1">Claim ID: {submitResult.claimId}</p>
            )}
          </div>
        )}
      </form>
    </div>
  );
}

