"use client";

import { useState, useEffect } from "react";
import { Claim } from "@/types/claim";
import { Star } from "lucide-react";
import Link from "next/link";

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
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function Dashboard() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchClaims();
    
    // Auto-refresh every 5 seconds to get new claims
    const interval = setInterval(() => {
      fetchClaims(false); // Don't show loading spinner on auto-refresh
    }, 5000);
    
    // Also listen for claim submissions from other tabs
    const handleStorageChange = () => {
      const claimSubmitted = localStorage.getItem("claimSubmitted");
      if (claimSubmitted) {
        // Refresh immediately when a claim is submitted
        fetchClaims(false);
        localStorage.removeItem("claimSubmitted");
      }
    };
    
    window.addEventListener("storage", handleStorageChange);
    
    // Check for claim submissions periodically (for same-tab submissions)
    const checkInterval = setInterval(() => {
      const claimSubmitted = localStorage.getItem("claimSubmitted");
      if (claimSubmitted) {
        fetchClaims(false);
        localStorage.removeItem("claimSubmitted");
      }
    }, 1000);
    
    return () => {
      clearInterval(interval);
      clearInterval(checkInterval);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  const fetchClaims = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const response = await fetch("http://localhost:8000/api/claims?limit=100");
      if (!response.ok) {
        throw new Error("Failed to fetch claims");
      }
      const data = await response.json();
      setClaims(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load claims");
      console.error("Error fetching claims:", err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <Link
            href="/"
            className="text-slate-600 hover:text-slate-900 mb-2 inline-block text-sm"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl font-bold text-slate-900">
            RiskChain Intelligence Dashboard
          </h1>
        </div>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          Incoming Claims
        </h2>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span className="inline-flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Auto-refreshing every 5 seconds
          </span>
        </div>
      </div>
      
      {loading && (
        <div className="text-center py-8 text-slate-600">Loading claims...</div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md mb-4">
          Error: {error}
        </div>
      )}
      
      {!loading && !error && claims.length === 0 && (
        <div className="text-center py-8 text-slate-600">
          No pending or unsettled claims found.
        </div>
      )}
      
      {!loading && !error && claims.length > 0 && (
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
                {claims.map((claim: Claim) => (
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
                      {claim.incidentDate ? formatDate(claim.incidentDate) : "N/A"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1">
                        {Array.from({ length: claim.urgency || 1 }).map((_, i) => (
                          <Star
                            key={i}
                            className="h-4 w-4 fill-amber-400 text-amber-400"
                          />
                        ))}
                        <span className="ml-1 text-sm text-slate-600">
                          {claim.urgency || 1}
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
      )}
    </div>
  );
}

