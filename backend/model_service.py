"""
Service to integrate the AI risk model for scoring claims.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add riskchain-ai to path
base_dir = Path(__file__).resolve().parent.parent
riskchain_ai_path = base_dir / "riskchain-ai"
sys.path.insert(0, str(riskchain_ai_path))

try:
    from graph_engine.graph_engine import GraphEngine
    from graph_engine.graph_features import GraphFeatures
    from risk_model import RiskModel, predict_risk
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI model not available: {e}")
    MODEL_AVAILABLE = False
    RiskModel = None
    GraphEngine = None
    GraphFeatures = None


class ModelService:
    """Service to score claims using the AI risk model."""
    
    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = artifacts_dir or str(riskchain_ai_path / "artifacts")
        self.model: Optional[RiskModel] = None
        self.graph_engine: Optional[GraphEngine] = None
        self._initialized = False
        
    def _initialize(self):
        """Initialize the model and graph engine."""
        if not MODEL_AVAILABLE:
            print("Warning: Model dependencies not available")
            return False
            
        if self._initialized:
            return True
            
        try:
            # Initialize model
            self.model = RiskModel(artifacts_dir=self.artifacts_dir)
            
            # Try to load pre-trained model
            model_path = os.path.join(self.artifacts_dir, "risk_model.pkl")
            if os.path.exists(model_path):
                try:
                    self.model.load()
                    if self.model.model is not None:
                        print(f"✅ Loaded pre-trained risk model: {type(self.model.model).__name__}")
                        self._initialized = True
                        return True
                    else:
                        print("Warning: Model file exists but model object is None")
                        return False
                except Exception as load_error:
                    error_msg = str(load_error)
                    # Check if it's a version compatibility issue
                    if "version" in error_msg.lower() or "unpickle" in error_msg.lower() or "attribute" in error_msg.lower():
                        print(f"⚠️  Model version compatibility issue: {error_msg}")
                        print("   Using fallback scoring instead.")
                    else:
                        print(f"Error loading model file: {error_msg}")
                        import traceback
                        traceback.print_exc()
                    return False
            else:
                print(f"Warning: No pre-trained model found at {model_path}. Using fallback scoring.")
                return False
                
        except Exception as e:
            print(f"Error initializing model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def build_graph_from_claims(self, claims: List[Dict[str, Any]]):
        """Build graph from all claims for graph-based features."""
        if not MODEL_AVAILABLE or not GraphEngine:
            return
            
        try:
            self.graph_engine = GraphEngine()
            self.graph_engine.build_graph(claims)
            print(f"Built graph with {len(claims)} claims")
        except Exception as e:
            print(f"Error building graph: {e}")
            self.graph_engine = None
    
    def score_claim(self, claim: Dict[str, Any], all_claims: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Score a single claim and return detailed risk breakdown.
        
        Returns:
            {
                "risk_score": float (0-100),
                "risk_category": str,
                "model_score": float,
                "graph_risk": float,
                "rule_adjustment": float,
                "breakdown": {
                    "provider_volume": int,
                    "lawyer_density": int,
                    "provider_lawyer_combo": int,
                    "ip_reuse": int,
                    "missing_docs": int,
                    "previous_claims": int,
                    "police_report": int
                },
                "features": {
                    "shared_ips": int,
                    "shared_doctors": int,
                    "shared_lawyers": int,
                    "graph_degree_centrality": float,
                    "graph_betweenness": float
                }
            }
        """
        if not self._initialize():
            # Fallback to basic scoring if model not available
            return self._fallback_score(claim)
        
        try:
            # Ensure graph is built if we have all claims
            if all_claims and not self.graph_engine:
                self.build_graph_from_claims(all_claims)
            
            # Convert claim to model format
            model_claim = self._convert_claim_for_model(claim)
            
            # Get model prediction
            if self.model and self.model.model:
                try:
                    # Ensure graph_engine is available for graph features
                    if not self.graph_engine and all_claims:
                        self.build_graph_from_claims(all_claims)
                    
                    model_scores = self.model.predict_proba([model_claim], graph_engine=self.graph_engine)
                    model_score = float(model_scores[0]) if model_scores and len(model_scores) > 0 else 0.5
                    # Debug: print first few claim fields to verify they're different
                    print(f"Model prediction for {model_claim.get('claim_id')}: {model_score:.4f} ({model_score*100:.2f}%) - age={model_claim.get('claimant_age')}, prev={model_claim.get('previous_claims_count')}, vehicle={model_claim.get('vehicle_make')} {model_claim.get('vehicle_year')}, provider={model_claim.get('medical_provider_name')[:15] if model_claim.get('medical_provider_name') and model_claim.get('medical_provider_name') != 'unknown' else 'None'}")
                except Exception as pred_error:
                    print(f"Error in model prediction: {pred_error}")
                    import traceback
                    traceback.print_exc()
                    model_score = 0.5
            else:
                print(f"Warning: Model not available for claim {model_claim.get('claim_id')}")
                model_score = 0.5
            
            # Get graph features and risk
            graph_risk = 0.0
            graph_features = {}
            breakdown = {}
            
            if self.graph_engine:
                gf = GraphFeatures(self.graph_engine)
                
                # Compute graph risk components
                provider = model_claim.get("medical_provider_name")
                lawyer = model_claim.get("lawyer_name")
                
                breakdown["provider_volume"] = gf.provider_volume_score(provider) if provider else 0
                breakdown["lawyer_density"] = gf.lawyer_density_score(lawyer) if lawyer else 0
                breakdown["provider_lawyer_combo"] = gf.provider_lawyer_combo_score(provider, lawyer) if (provider and lawyer) else 0
                breakdown["ip_reuse"] = gf.ip_reuse_score(model_claim)
                
                graph_risk = gf.compute_graph_risk(model_claim)
                
                # Get graph features
                features_df = gf.compute_features_for_claims([model_claim])
                if not features_df.empty:
                    row = features_df.iloc[0]
                    graph_features = {
                        "shared_ips": int(row.get("shared_ips", 0)),
                        "shared_doctors": int(row.get("shared_doctors", 0)),
                        "shared_lawyers": int(row.get("shared_lawyers", 0)),
                        "graph_degree_centrality": float(row.get("graph_degree_centrality", 0.0)),
                        "graph_betweenness": float(row.get("graph_betweenness", 0.0))
                    }
            
            # Rule-based adjustments
            rule_adj = self._compute_rule_adjustment(model_claim)
            breakdown["missing_docs"] = 5 if not model_claim.get("police_report_filed") else 0
            breakdown["previous_claims"] = 0
            breakdown["police_report"] = 0 if model_claim.get("police_report_filed") else 5
            
            # Calculate final score (0-100)
            # Model contributes 70%, graph risk contributes 20%, rules contribute 10%
            # model_score is already a probability [0,1], so multiply by 70 to get contribution
            model_contribution = model_score * 70
            graph_contribution = (graph_risk / 30.0) * 20 if graph_risk > 0 else 0
            final_score = min(100.0, model_contribution + graph_contribution + rule_adj)
            
            # Determine risk category
            if final_score >= 70:
                risk_category = "high"
            elif final_score >= 31:
                risk_category = "medium"
            else:
                risk_category = "low"
            
            return {
                "risk_score": round(final_score, 2),
                "risk_category": risk_category,
                "model_score": round(model_score * 100, 2),
                "graph_risk": round(graph_risk, 2),
                "rule_adjustment": round(rule_adj, 2),
                "breakdown": breakdown,
                "features": graph_features
            }
            
        except Exception as e:
            print(f"Error scoring claim: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_score(claim)
    
    def _convert_claim_for_model(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database claim format to model format."""
        # Handle date conversions
        accident_date = claim.get("accident_date")
        if isinstance(accident_date, datetime):
            accident_date = accident_date.isoformat()[:10]  # YYYY-MM-DD
        elif accident_date and isinstance(accident_date, str):
            try:
                # Try to parse and reformat
                dt = datetime.fromisoformat(accident_date.replace('Z', '+00:00'))
                accident_date = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        claim_submission_date = claim.get("claim_submission_date")
        if isinstance(claim_submission_date, datetime):
            claim_submission_date = claim_submission_date.isoformat()[:10]
        elif claim_submission_date and isinstance(claim_submission_date, str):
            try:
                dt = datetime.fromisoformat(claim_submission_date.replace('Z', '+00:00'))
                claim_submission_date = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        # Build model claim dict - preserve actual values, only default when truly missing
        # Helper to get value with proper handling of None/empty
        def get_val(key, default=None, convert_int=False, convert_float=False):
            val = claim.get(key)
            if val is None:
                return default
            if val == "" or (isinstance(val, str) and val.lower() == "none"):
                return default
            if convert_int:
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default
            if convert_float:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default
            return val
        
        model_claim = {
            "claim_id": get_val("claim_id", ""),
            "claim_submission_date": claim_submission_date or "",
            "accident_date": accident_date or "",
            "accident_time": get_val("accident_time", ""),
            "accident_location_city": get_val("accident_location_city", ""),
            "accident_location_state": get_val("accident_location_state", ""),
            "accident_description": get_val("accident_description", "") or "",
            "police_report_filed": get_val("police_report_filed", 0, convert_int=True),
            "loss_type": get_val("loss_type", "unknown"),
            "claimant_name": get_val("claimant_name", ""),
            "claimant_age": get_val("claimant_age", 0, convert_int=True),
            "claimant_gender": get_val("claimant_gender", "unknown"),
            "claimant_city": get_val("claimant_city", ""),
            "claimant_state": get_val("claimant_state", "unknown"),
            "vehicle_make": get_val("vehicle_make", "unknown"),
            "vehicle_model": get_val("vehicle_model", "unknown"),
            "vehicle_year": get_val("vehicle_year", 0, convert_int=True),
            "vehicle_use_type": get_val("vehicle_use_type", "unknown"),
            "vehicle_mileage": get_val("vehicle_mileage", 0, convert_int=True),
            "damage_severity": get_val("damage_severity", "unknown"),
            "injury_severity": get_val("injury_severity", "unknown"),
            "medical_treatment_received": get_val("medical_treatment_received", 0, convert_int=True),
            "medical_cost_estimate": get_val("medical_cost_estimate", 0.0, convert_float=True),
            "airbags_deployed": get_val("airbags_deployed", 0, convert_int=True),
            "policy_tenure_months": get_val("policy_tenure_months", 0, convert_int=True),
            "coverage_type": get_val("coverage_type", "unknown"),
            "policy_type": get_val("policy_type", "unknown"),
            "deductible_amount": get_val("deductible_amount", 0.0, convert_float=True),
            "previous_claims_count": get_val("previous_claims_count", 0, convert_int=True),
            "lawyer_name": get_val("lawyer_name", "unknown"),
            "medical_provider_name": get_val("medical_provider_name", "unknown"),
            "repair_shop_name": get_val("repair_shop_name", ""),
            "reported_by": get_val("reported_by", ""),
            "ip_address": get_val("ip_address", ""),
            # Calculate claim_amount from medical_cost_estimate or use a default based on damage
            "claim_amount": float(get_val("medical_cost_estimate", 0) or 0) * 1.5 if get_val("medical_cost_estimate") else (10000.0 if get_val("damage_severity") in ["major", "total_loss"] else 5000.0),
        }
        
        return model_claim
    
    def _compute_rule_adjustment(self, claim: Dict[str, Any]) -> float:
        """Compute rule-based risk adjustment."""
        adj = 0.0
        if claim.get("police_report_filed") == 0:
            adj += 5
        if claim.get("medical_provider_name") and claim.get("lawyer_name"):
            adj += 3
        return adj
    
    def _fallback_score(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scoring when model is not available."""
        score = 0
        if not claim.get("police_report_filed"):
            score += 10
        if claim.get("medical_provider_name") and claim.get("lawyer_name"):
            score += 10
        
        if score >= 70:
            category = "high"
        elif score >= 31:
            category = "medium"
        else:
            category = "low"
        
        return {
            "risk_score": min(100, score),
            "risk_category": category,
            "model_score": 0.0,
            "graph_risk": 0.0,
            "rule_adjustment": float(score),
            "breakdown": {
                "provider_volume": 0,
                "lawyer_density": 0,
                "provider_lawyer_combo": 0,
                "ip_reuse": 0,
                "missing_docs": 5 if not claim.get("police_report_filed") else 0,
                "previous_claims": 0,
                "police_report": 0 if claim.get("police_report_filed") else 5
            },
            "features": {}
        }


# Global instance
_model_service = None

def get_model_service() -> ModelService:
    """Get or create the global model service instance."""
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service

