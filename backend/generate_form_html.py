"""
Generate comprehensive form HTML matching CSV dataset fields
"""

form_sections = {
    "I. Claim Identification": [
        ("policy_number", "Insurance Policy Number", "text", "Enter policy number"),
    ],
    "II. Dates and Times": [
        ("claim_submission_date", "Claim Submission Date", "date", ""),
        ("accident_date", "Date of Accident", "date", ""),
        ("accident_time", "Time of Accident", "time", "HH:MM format"),
    ],
    "III. Location Information": [
        ("accident_location_city", "Accident Location - City", "text", "City where accident occurred"),
        ("accident_location_state", "Accident Location - State", "text", "State where accident occurred (e.g., CA, NY)"),
    ],
    "IV. Claimant Information": [
        ("claimant_age", "Claimant Age", "number", "Enter age"),
        ("claimant_gender", "Claimant Gender", "select", "", ["", "male", "female", "other"]),
        ("claimant_city", "Claimant City", "text", "City of residence"),
        ("claimant_state", "Claimant State", "text", "State of residence"),
    ],
    "V. Vehicle Information": [
        ("vehicle_make", "Vehicle Make", "text", "e.g., Toyota, Honda, Ford"),
        ("vehicle_model", "Vehicle Model", "text", "e.g., Camry, Accord, F-150"),
        ("vehicle_year", "Vehicle Year", "number", "e.g., 2020"),
        ("vehicle_use_type", "Vehicle Use Type", "select", "", ["", "personal", "commercial"]),
        ("vehicle_mileage", "Vehicle Mileage", "number", "Current odometer reading"),
    ],
    "VI. Incident Details": [
        ("loss_type", "Loss Type", "select", "", ["", "collision", "comprehensive", "liability", "other"]),
        ("accident_description", "Accident Description", "textarea", "Provide detailed description of the accident"),
        ("police_report_filed", "Police Report Filed", "select", "", ["", "0", "1"]),
    ],
    "VII. Damage and Injury Information": [
        ("damage_severity", "Damage Severity", "select", "", ["", "minor", "moderate", "major", "total_loss"]),
        ("injury_severity", "Injury Severity", "select", "", ["", "none", "minor", "moderate", "severe"]),
        ("medical_treatment_received", "Medical Treatment Received", "select", "", ["", "0", "1"]),
        ("medical_cost_estimate", "Medical Cost Estimate ($)", "number", "Estimated medical costs"),
        ("airbags_deployed", "Airbags Deployed", "select", "", ["", "0", "1"]),
    ],
    "VIII. Policy Information": [
        ("policy_tenure_months", "Policy Tenure (Months)", "number", "Number of months policy has been active"),
        ("coverage_type", "Coverage Type", "select", "", ["", "collision", "comprehensive", "liability_only", "full_coverage"]),
        ("policy_type", "Policy Type", "select", "", ["", "collision_only", "comprehensive_only", "liability_only", "full"]),
        ("deductible_amount", "Deductible Amount ($)", "number", "Deductible amount"),
        ("previous_claims_count", "Previous Claims Count", "number", "Number of previous claims"),
    ],
    "IX. Service Providers": [
        ("lawyer_name", "Lawyer/Attorney Name", "text", "Name of legal representative"),
        ("medical_provider_name", "Medical Provider Name", "text", "Name of medical provider/facility"),
        ("repair_shop_name", "Repair Shop Name", "text", "Name of repair shop"),
        ("reported_by", "Reported By", "select", "", ["", "self", "agent", "third_party"]),
    ],
    "X. Additional Information": [
        ("photos", "Photo URL", "text", "URL to accident photos"),
        ("status", "Claim Status", "select", "", ["pending", "under_review", "approved", "denied", "settled"]),
    ],
}

def generate_form_html():
    """Generate form HTML with all CSV fields."""
    html_parts = []
    
    for section_title, fields in form_sections.items():
        html_parts.append(f'                    <div class="section">')
        html_parts.append(f'                        <div class="section-title">{section_title}</div>')
        html_parts.append('')
        
        for field_info in fields:
            field_name = field_info[0]
            field_label = field_info[1]
            field_type = field_info[2]
            field_placeholder = field_info[3] if len(field_info) > 3 else ""
            field_options = field_info[4] if len(field_info) > 4 else []
            
            html_parts.append('                        <div class="form-group">')
            html_parts.append(f'                            <label>{field_label}</label>')
            
            if field_type == "select":
                html_parts.append(f'                            <select name="{field_name}">')
                for option in field_options:
                    if option == "":
                        html_parts.append(f'                                <option value="">-- Please Select --</option>')
                    else:
                        display = option.replace("_", " ").title()
                        html_parts.append(f'                                <option value="{option}">{display}</option>')
                html_parts.append('                            </select>')
            elif field_type == "textarea":
                html_parts.append(f'                            <textarea name="{field_name}" rows="4" placeholder="{field_placeholder}"></textarea>')
            else:
                input_attrs = f'name="{field_name}" type="{field_type}"'
                if field_placeholder:
                    input_attrs += f' placeholder="{field_placeholder}"'
                if field_type == "number":
                    input_attrs += ' step="0.01"'
                html_parts.append(f'                            <input {input_attrs}>')
            
            if field_placeholder and field_type != "textarea":
                html_parts.append(f'                            <small>{field_placeholder}</small>')
            
            html_parts.append('                        </div>')
            html_parts.append('')
        
        html_parts.append('                    </div>')
        html_parts.append('')
    
    return '\n'.join(html_parts)

if __name__ == "__main__":
    print(generate_form_html())

