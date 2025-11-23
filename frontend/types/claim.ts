export type ClaimStatus = "New" | "Review" | "Approved" | "Rejected" | "pending" | "unsettled" | "under_review" | "approved" | "denied" | "settled";

export interface Claim {
  id: string;
  claimantName: string;
  policyNumber: string;
  incidentDate: string;
  incidentType: string;
  status: ClaimStatus;
  riskScore: number;
  urgency: number;
  missingDocs: string[];
}

