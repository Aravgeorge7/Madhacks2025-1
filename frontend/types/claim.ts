export type ClaimStatus = "New" | "Review" | "Approved" | "Rejected";

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

