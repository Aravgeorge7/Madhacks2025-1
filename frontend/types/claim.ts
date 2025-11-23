export type ClaimStatus = "New" | "Review" | "Approved" | "Rejected" | "pending" | "unsettled" | "under_review" | "approved" | "denied" | "settled";

export interface RiskBreakdown {
  provider_volume: number;
  lawyer_density: number;
  provider_lawyer_combo: number;
  ip_reuse: number;
  missing_docs: number;
  previous_claims: number;
  police_report: number;
}

export interface GraphFeatures {
  shared_ips: number;
  shared_doctors: number;
  shared_lawyers: number;
  graph_degree_centrality: number;
  graph_betweenness: number;
}

export interface ModelDetails {
  model_score: number;
  graph_risk: number;
  rule_adjustment: number;
}

export interface Claim {
  id: number | string;
  claim_id?: string;
  claimantName: string;
  policyNumber: string;
  incidentDate: string;
  incidentType: string;
  status: ClaimStatus;
  riskScore: number;
  urgency: number;
  missingDocs: string[];
  // Model scoring fields
  modelRiskScore?: number;
  modelRiskCategory?: string;
  riskBreakdown?: RiskBreakdown;
  graphFeatures?: GraphFeatures;
  modelDetails?: ModelDetails;
}
