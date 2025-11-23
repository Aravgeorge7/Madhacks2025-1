"use client";

import { MOCK_CLAIMS } from "@/data/mockClaims";
import { Claim } from "@/types/claim";
import { Star } from "lucide-react";
import ClaimForm from "@/components/ClaimForm";

function getRiskBadgeColor(riskScore: number): string {
  if (riskScore < 30) {
    return "bg-emerald-500 text-white";
  } else if (riskScore <= 70) {
    return "bg-amber-500 text-white";
  } else {
    return "bg-red-500 text-white";
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function Home() {
  return (
    <div className="h-full overflow-auto p-8">
      <h1 className="mb-6 text-3xl font-bold text-slate-900">
        RiskChain Intelligence
      </h1>
      
      {/* Claim Submission Form */}
      <ClaimForm />
      
      <h2 className="mb-6 text-2xl font-bold text-slate-900 mt-8">
        Incoming Claims
      </h2>
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Claimant
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Type
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Date
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Urgency
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Risk Score
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {MOCK_CLAIMS.map((claim: Claim) => (
                <tr
                  key={claim.id}
                  className="transition-colors hover:bg-slate-50"
                >
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-slate-900">
                      {claim.claimantName}
                    </div>
                    <div className="text-xs text-slate-500">
                      {claim.policyNumber}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-700">
                    {claim.incidentType}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-700">
                    {formatDate(claim.incidentDate)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: claim.urgency }).map((_, i) => (
                        <Star
                          key={i}
                          className="h-4 w-4 fill-amber-400 text-amber-400"
                        />
                      ))}
                      <span className="ml-1 text-sm text-slate-600">
                        {claim.urgency}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${getRiskBadgeColor(claim.riskScore)}`}
                    >
                      {claim.riskScore}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center rounded-md bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-800">
                      {claim.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {claim.riskScore > 70 && (
                      <button className="rounded-md bg-slate-900 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-slate-800">
                        View Graph
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
