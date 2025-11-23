"use client";

import { useState, useEffect } from "react";
import { Claim } from "@/types/claim";
import { Star, Shield, AlertTriangle, CheckCircle, Info, TrendingUp, Users, FileWarning } from "lucide-react";
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

function getRiskGradient(riskScore: number): string {
  if (riskScore < 30) {
    return "from-emerald-600 to-emerald-800";
  } else if (riskScore <= 70) {
    return "from-amber-500 to-orange-600";
  } else {
    return "from-red-500 to-red-700";
  }
}

function getRiskIcon(riskScore: number) {
  if (riskScore < 30) {
    return <CheckCircle className="h-5 w-5 text-emerald-400" />;
  } else if (riskScore <= 70) {
    return <AlertTriangle className="h-5 w-5 text-amber-400" />;
  } else {
    return <Shield className="h-5 w-5 text-red-400" />;
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
                    AI Model Score
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
                      <Link
                        href={`/form?claimId=${claim.id}&prefill=true`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        {claim.claimantName}
                      </Link>
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
                      {claim.modelRiskScore !== undefined ? (
                        <div className="relative group">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold cursor-help shadow-sm transition-all duration-200 hover:scale-105 ${getRiskBadgeColor(claim.modelRiskScore)}`}
                          >
                            <span className="text-sm">{Math.round(claim.modelRiskScore)}</span>
                            <span className="text-[10px] opacity-80">/100</span>
                          </span>

                          {/* Professional Hover Tooltip */}
                          <div className="absolute left-0 top-full mt-3 w-96 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform group-hover:translate-y-0 translate-y-2">
                            {/* Header with gradient */}
                            <div className={`bg-gradient-to-r ${getRiskGradient(claim.modelRiskScore)} rounded-t-xl px-5 py-4`}>
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  {getRiskIcon(claim.modelRiskScore)}
                                  <div>
                                    <h3 className="text-white font-bold text-sm tracking-wide">AI RISK ASSESSMENT</h3>
                                    <p className="text-white/80 text-xs mt-0.5">Powered by RiskChain Intelligence</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="text-3xl font-black text-white">{Math.round(claim.modelRiskScore)}</div>
                                  <div className="text-xs text-white/70 uppercase tracking-wider">{claim.modelRiskCategory || 'Unknown'} Risk</div>
                                </div>
                              </div>
                            </div>

                            <div className="p-5 space-y-4">
                              {/* Score Breakdown */}
                              {claim.modelDetails && (
                                <div className="bg-slate-50 rounded-lg p-4">
                                  <div className="flex items-center gap-2 mb-3">
                                    <TrendingUp className="h-4 w-4 text-slate-600" />
                                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide">Score Components</h4>
                                  </div>
                                  <div className="space-y-2.5">
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-600">ML Model Prediction</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-blue-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.model_score, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-800 w-12 text-right">{claim.modelDetails.model_score.toFixed(1)}%</span>
                                      </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-600">Network Analysis</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-purple-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.graph_risk * 3.33, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-800 w-12 text-right">{claim.modelDetails.graph_risk.toFixed(1)}</span>
                                      </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-600">Rule-Based Flags</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-orange-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.rule_adjustment * 7.7, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-800 w-12 text-right">+{claim.modelDetails.rule_adjustment.toFixed(0)}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Risk Factors */}
                              {(claim.riskBreakdown || claim.modelDetails || claim.graphFeatures) && (
                                <div>
                                  <div className="flex items-center gap-2 mb-3">
                                    <FileWarning className="h-4 w-4 text-red-500" />
                                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide">Identified Risk Factors</h4>
                                  </div>
                                  <div className="grid grid-cols-2 gap-2">
                                    {/* HIGH PRIORITY: ML Model detected fraud patterns */}
                                    {claim.modelDetails && claim.modelDetails.model_score > 70 && (
                                      <div className="col-span-2 flex items-center gap-2 bg-red-50 border border-red-200 rounded-md px-2.5 py-2">
                                        <Shield className="h-4 w-4 text-red-600" />
                                        <div>
                                          <span className="text-xs font-semibold text-red-700">AI Fraud Pattern Detected</span>
                                          <span className="text-[10px] text-red-600 ml-1">({claim.modelDetails.model_score.toFixed(0)}% confidence)</span>
                                        </div>
                                      </div>
                                    )}

                                    {/* Network-based risks - shared entities indicate fraud rings */}
                                    {claim.graphFeatures && claim.graphFeatures.shared_doctors > 0 && (
                                      <div className="flex items-center gap-2 bg-indigo-50 border border-indigo-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                                        <span className="text-xs text-indigo-700">Shared Provider Network ({claim.graphFeatures.shared_doctors})</span>
                                      </div>
                                    )}
                                    {claim.graphFeatures && claim.graphFeatures.shared_lawyers > 0 && (
                                      <div className="flex items-center gap-2 bg-indigo-50 border border-indigo-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                                        <span className="text-xs text-indigo-700">Shared Attorney Network ({claim.graphFeatures.shared_lawyers})</span>
                                      </div>
                                    )}
                                    {claim.graphFeatures && claim.graphFeatures.shared_ips > 0 && (
                                      <div className="flex items-center gap-2 bg-purple-50 border border-purple-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                                        <span className="text-xs text-purple-700">Shared IP Address ({claim.graphFeatures.shared_ips})</span>
                                      </div>
                                    )}

                                    {/* Rule-based flags */}
                                    {claim.riskBreakdown?.police_report > 0 && (
                                      <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                        <span className="text-xs text-red-700">No Police Report</span>
                                      </div>
                                    )}
                                    {claim.riskBreakdown?.previous_claims > 0 && (
                                      <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                        <span className="text-xs text-red-700">Multiple Prior Claims</span>
                                      </div>
                                    )}
                                    {claim.riskBreakdown?.provider_volume > 0 && (
                                      <div className="flex items-center gap-2 bg-amber-50 border border-amber-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-700">High-Volume Provider</span>
                                      </div>
                                    )}
                                    {claim.riskBreakdown?.lawyer_density > 0 && (
                                      <div className="flex items-center gap-2 bg-amber-50 border border-amber-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-700">High-Volume Attorney</span>
                                      </div>
                                    )}
                                    {claim.riskBreakdown?.provider_lawyer_combo > 0 && (
                                      <div className="flex items-center gap-2 bg-orange-50 border border-orange-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                                        <span className="text-xs text-orange-700">Provider-Attorney Collusion</span>
                                      </div>
                                    )}
                                    {claim.riskBreakdown?.ip_reuse > 0 && (
                                      <div className="flex items-center gap-2 bg-purple-50 border border-purple-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                                        <span className="text-xs text-purple-700">IP Address Anomaly</span>
                                      </div>
                                    )}

                                    {/* Legal representation flag (from rule adjustment) */}
                                    {claim.modelDetails && claim.modelDetails.rule_adjustment >= 3 &&
                                     !claim.riskBreakdown?.police_report && !claim.riskBreakdown?.previous_claims && (
                                      <div className="flex items-center gap-2 bg-amber-50 border border-amber-100 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-700">Legal Representation Present</span>
                                      </div>
                                    )}

                                    {/* Only show "no risk factors" if EVERYTHING is clean */}
                                    {(!claim.modelDetails || claim.modelDetails.model_score <= 30) &&
                                     (!claim.graphFeatures || (claim.graphFeatures.shared_doctors === 0 && claim.graphFeatures.shared_lawyers === 0 && claim.graphFeatures.shared_ips === 0)) &&
                                     (!claim.riskBreakdown || (!claim.riskBreakdown.police_report && !claim.riskBreakdown.previous_claims &&
                                     !claim.riskBreakdown.provider_volume && !claim.riskBreakdown.lawyer_density &&
                                     !claim.riskBreakdown.provider_lawyer_combo && !claim.riskBreakdown.ip_reuse)) &&
                                     (!claim.modelDetails || claim.modelDetails.rule_adjustment < 3) && (
                                      <div className="col-span-2 flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-md px-2.5 py-1.5">
                                        <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                                        <span className="text-xs text-emerald-700">No significant risk factors identified</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Network Analysis Summary - show graph metrics */}
                              {claim.graphFeatures && (
                                <div className="border-t border-slate-100 pt-4">
                                  <div className="flex items-center gap-2 mb-3">
                                    <Users className="h-4 w-4 text-indigo-500" />
                                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide">Network Analysis</h4>
                                  </div>
                                  <div className="grid grid-cols-3 gap-3">
                                    <div className="text-center bg-slate-50 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_doctors > 0 ? 'text-indigo-600' : 'text-slate-400'}`}>
                                        {claim.graphFeatures.shared_doctors}
                                      </div>
                                      <div className="text-[10px] text-slate-500 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-400">(via Provider)</div>
                                    </div>
                                    <div className="text-center bg-slate-50 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_lawyers > 0 ? 'text-indigo-600' : 'text-slate-400'}`}>
                                        {claim.graphFeatures.shared_lawyers}
                                      </div>
                                      <div className="text-[10px] text-slate-500 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-400">(via Attorney)</div>
                                    </div>
                                    <div className="text-center bg-slate-50 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_ips > 0 ? 'text-purple-600' : 'text-slate-400'}`}>
                                        {claim.graphFeatures.shared_ips}
                                      </div>
                                      <div className="text-[10px] text-slate-500 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-400">(via IP)</div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Footer */}
                            <div className="bg-slate-50 rounded-b-xl px-5 py-3 border-t border-slate-100">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
                                  <Info className="h-3 w-3" />
                                  <span>AI-powered fraud detection analysis</span>
                                </div>
                                <div className="text-[10px] font-medium text-slate-600 uppercase tracking-wider">
                                  Confidence: High
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
                          <span className="text-xs text-slate-400">Analyzing...</span>
                        </div>
                      )}
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

