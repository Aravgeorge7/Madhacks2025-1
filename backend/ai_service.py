"""
AI Service for claim text analysis and consistency checking.
Uses GPT-4o-mini to analyze accident descriptions and compare against metadata.
"""

import os
from typing import Dict, Any, Optional
from models import ClaimFormData

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")


def analyze_claim_text(claim_data: ClaimFormData) -> Dict[str, Any]:
    """
    Analyze claim text using GPT-4o-mini for consistency checking and fraud detection.
    
    Compares the accident description against reported metadata to detect inconsistencies.
    
    Args:
        claim_data: Full ClaimFormData Pydantic model containing all claim information
        
    Returns:
        Dictionary with:
        - fraud_nlp_score: Integer 0-20 representing fraud risk from text analysis
        - consistency_flags: List of detected inconsistencies
        - analysis_summary: Text summary of the analysis
    """
    
    if not OPENAI_AVAILABLE:
        # Fallback: Return basic score if OpenAI is not available
        return {
            "fraud_nlp_score": 0,
            "consistency_flags": [],
            "analysis_summary": "OpenAI library not available. Install with: pip install openai"
        }
    
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Returning default score.")
        return {
            "fraud_nlp_score": 0,
            "consistency_flags": [],
            "analysis_summary": "OpenAI API key not configured"
        }
    
    # Extract relevant fields for consistency checking
    accident_description = claim_data.accident_description or claim_data.description or ""
    injury_severity = claim_data.injury_severity or "Unknown"
    damage_severity = claim_data.damage_severity or "Unknown"
    accident_time = claim_data.accident_time or "Unknown"
    loss_type = claim_data.loss_type or "Unknown"
    
    # Build the prompt for GPT-4o-mini
    prompt = f"""You are an insurance fraud detection AI. Analyze the following claim for inconsistencies and fraud indicators.

CLAIMANT'S ACCIDENT DESCRIPTION:
{accident_description}

REPORTED METADATA:
- Injury Severity: {injury_severity}
- Damage Severity: {damage_severity}
- Accident Time: {accident_time}
- Loss Type: {loss_type}

TASK: Compare the claimant's Accident Description against their Reported Metadata.

CONSISTENCY CHECKING RULES:
1. If the description describes major injuries (broken bones, fractures, severe trauma, spinal injuries, head injuries) but they selected 'Minor Injury' or 'No Injury' in the form, Flag this as HIGH RISK (Consistency mismatch).

2. If they claim it was a 'Hit and Run' in text but selected 'Collision' with another driver, Flag it.

3. If the description mentions severe vehicle damage (totaled, extensive damage, frame damage) but they selected 'Minor Damage' or 'No Damage', Flag it.

4. If the description tone is suspicious (urgent money requests, inconsistent details, vague descriptions), increase risk score.

5. If the description contains trigger phrases like "give me money", "need cash fast", or ends with "...", increase risk score.

ANALYSIS REQUIREMENTS:
- Analyze the tone and language used in the description
- Check for consistency between description and metadata
- Identify any red flags or suspicious patterns
- Provide a fraud risk score from 0-20 where:
  * 0-5: Low risk, consistent and normal
  * 6-10: Moderate risk, minor inconsistencies
  * 11-15: High risk, significant inconsistencies or suspicious patterns
  * 16-20: Very high risk, major inconsistencies or clear fraud indicators

RESPOND IN JSON FORMAT:
{{
    "fraud_nlp_score": <integer 0-20>,
    "consistency_flags": [<list of detected inconsistencies>],
    "tone_analysis": "<brief analysis of claimant's tone>",
    "risk_factors": [<list of specific risk factors found>],
    "analysis_summary": "<brief summary of findings>"
}}
"""

    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert insurance fraud detection AI. Analyze claims for inconsistencies and fraud indicators. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=500
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        try:
            analysis_result = json.loads(response_text)
            
            # Extract and validate the fraud_nlp_score
            fraud_nlp_score = analysis_result.get("fraud_nlp_score", 0)
            # Ensure it's between 0-20
            fraud_nlp_score = max(0, min(20, int(fraud_nlp_score)))
            
            return {
                "fraud_nlp_score": fraud_nlp_score,
                "consistency_flags": analysis_result.get("consistency_flags", []),
                "tone_analysis": analysis_result.get("tone_analysis", ""),
                "risk_factors": analysis_result.get("risk_factors", []),
                "analysis_summary": analysis_result.get("analysis_summary", "")
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response from OpenAI: {e}")
            print(f"Response text: {response_text}")
            # Fallback: Try to extract score from text
            score_match = re.search(r'"fraud_nlp_score"\s*:\s*(\d+)', response_text)
            if score_match:
                fraud_nlp_score = max(0, min(20, int(score_match.group(1))))
            else:
                fraud_nlp_score = 0
            
            return {
                "fraud_nlp_score": fraud_nlp_score,
                "consistency_flags": ["Error parsing AI response"],
                "analysis_summary": f"AI analysis completed but response parsing failed: {str(e)}"
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "fraud_nlp_score": 0,
            "consistency_flags": [],
            "analysis_summary": f"Error during AI analysis: {str(e)}"
        }

