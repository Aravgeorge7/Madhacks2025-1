"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Claim } from "@/types/claim";
import { Star, Shield, AlertTriangle, CheckCircle, Info, TrendingUp, Users, FileWarning, Inbox, LogOut } from "lucide-react";
import Link from "next/link";
import { isAuthenticated, logout } from "@/lib/auth";
import { useClaimsData } from "@/hooks/useClaimsData";

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
  const router = useRouter();
  const [authChecked, setAuthChecked] = useState(false);
  const REFRESH_INTERVAL = 10_000;
  const { claims, loading, error } = useClaimsData({
    enabled: authChecked,
    pollInterval: REFRESH_INTERVAL,
    limit: 100,
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    setAuthChecked(true);
  }, [router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!authChecked) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-black">
      <div className="sticky top-0 z-40 bg-black/95 backdrop-blur-md border-b border-slate-800 shadow-lg">
        <div className="px-8 py-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <Link
                href="/"
                className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-3 text-sm font-medium transition-colors group"
              >
                <svg
                  className="w-4 h-4 group-hover:-translate-x-1 transition-transform"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                Back to Home
              </Link>
              <h1 className="text-4xl font-bold text-white tracking-tight">
                RiskChain Intelligence Dashboard
              </h1>
              <p className="text-slate-400 mt-2 font-medium">
                Comprehensive fraud detection and risk analysis platform
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
          
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-white">
              Incoming Claims
            </h2>
            <div className="flex items-center gap-3 px-4 py-2 bg-green-900/30 border border-green-700/50 rounded-lg">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-medium text-green-400">
                Auto-refreshing every {Math.round(REFRESH_INTERVAL / 1000)} seconds
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8">
        {loading && (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-12 h-12 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin mb-4"></div>
          <p className="text-slate-400 font-medium">Loading claims...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-red-900/20 border-2 border-red-800 text-red-400 px-6 py-4 rounded-xl mb-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <div>
              <p className="font-semibold">Error loading claims</p>
              <p className="text-sm text-red-400">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {!loading && !error && claims.length === 0 && (
        <div className="text-center py-16 bg-slate-900 rounded-2xl border border-slate-800">
          <Inbox className="w-16 h-16 text-slate-700 mx-auto mb-4" />
          <p className="text-slate-300 font-medium text-lg">No pending or unsettled claims found</p>
          <p className="text-slate-500 text-sm mt-2">New claims will appear here automatically</p>
        </div>
      )}
      
      {!loading && !error && claims.length > 0 && (
        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Claimant
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Urgency
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Risk Score
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    AI Model Score
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900">
                {claims.map((claim: Claim) => (
                  <tr
                    key={claim.id}
                    className="transition-all duration-200 hover:bg-slate-800/50"
                  >
                    <td className="px-6 py-4">
                      <Link
                        href={`/form?claimId=${claim.id}&prefill=true`}
                        className="text-sm font-semibold text-blue-400 hover:text-blue-300 hover:underline cursor-pointer transition-colors"
                      >
                        {claim.claimantName}
                      </Link>
                      <div className="text-xs text-slate-500 mt-1 font-mono">
                        {claim.policyNumber}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 capitalize border border-slate-700">
                        {claim.incidentType}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300 font-medium">
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
                        <span className="ml-1 text-sm text-slate-400">
                          {claim.urgency || 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center justify-center rounded-full px-3 py-1.5 text-xs font-bold shadow-sm ${getRiskBadgeColor(claim.riskScore)}`}
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
                          <div className="absolute left-0 top-full mt-3 w-96 bg-slate-900 rounded-xl shadow-2xl border border-slate-700 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform group-hover:translate-y-0 translate-y-2">
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
                              {claim.modelDetails && (
                                <div className="bg-slate-800 rounded-lg p-4">
                                  <div className="flex items-center gap-2 mb-3">
                                    <TrendingUp className="h-4 w-4 text-slate-400" />
                                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide">Score Components</h4>
                                  </div>
                                  <div className="space-y-2.5">
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-400">ML Model Prediction</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-blue-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.model_score, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-200 w-12 text-right">{claim.modelDetails.model_score.toFixed(1)}%</span>
                                      </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-400">Network Analysis</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-purple-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.graph_risk * 3.33, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-200 w-12 text-right">{claim.modelDetails.graph_risk.toFixed(1)}</span>
                                      </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-xs text-slate-400">Rule-Based Flags</span>
                                      <div className="flex items-center gap-2">
                                        <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-orange-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(claim.modelDetails.rule_adjustment * 7.7, 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-xs font-semibold text-slate-200 w-12 text-right">+{claim.modelDetails.rule_adjustment.toFixed(0)}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {(claim.riskBreakdown || claim.modelDetails || claim.graphFeatures) && (
                                <div>
                                  <div className="flex items-center gap-2 mb-3">
                                    <FileWarning className="h-4 w-4 text-red-500" />
                                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide">Identified Risk Factors</h4>
                                  </div>
                                  <div className="grid grid-cols-2 gap-2">
                                    {/* HIGH PRIORITY: ML Model detected fraud patterns */}
                                    {claim.modelDetails && claim.modelDetails.model_score > 70 && (
                                      <div className="col-span-2 flex items-center gap-2 bg-red-900/30 border border-red-800 rounded-md px-2.5 py-2">
                                        <Shield className="h-4 w-4 text-red-400" />
                                        <div>
                                          <span className="text-xs font-semibold text-red-300">AI Fraud Pattern Detected</span>
                                          <span className="text-[10px] text-red-400 ml-1">({claim.modelDetails.model_score.toFixed(0)}% confidence)</span>
                                        </div>
                                      </div>
                                    )}

                                    {claim.graphFeatures && claim.graphFeatures.shared_doctors > 0 && (
                                      <div className="flex items-center gap-2 bg-indigo-900/30 border border-indigo-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                                        <span className="text-xs text-indigo-300">Shared Provider Network ({claim.graphFeatures.shared_doctors})</span>
                                      </div>
                                    )}
                                    {claim.graphFeatures && claim.graphFeatures.shared_lawyers > 0 && (
                                      <div className="flex items-center gap-2 bg-indigo-900/30 border border-indigo-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                                        <span className="text-xs text-indigo-300">Shared Attorney Network ({claim.graphFeatures.shared_lawyers})</span>
                                      </div>
                                    )}
                                    {claim.graphFeatures && claim.graphFeatures.shared_ips > 0 && (
                                      <div className="flex items-center gap-2 bg-purple-900/30 border border-purple-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                                        <span className="text-xs text-purple-300">Shared IP Address ({claim.graphFeatures.shared_ips})</span>
                                      </div>
                                    )}

                                    {(claim.riskBreakdown?.police_report ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-red-900/30 border border-red-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                        <span className="text-xs text-red-300">No Police Report</span>
                                      </div>
                                    )}
                                    {(claim.riskBreakdown?.previous_claims ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-red-900/30 border border-red-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                        <span className="text-xs text-red-300">Multiple Prior Claims</span>
                                      </div>
                                    )}
                                    {(claim.riskBreakdown?.provider_volume ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-amber-900/30 border border-amber-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-300">High-Volume Provider</span>
                                      </div>
                                    )}
                                    {(claim.riskBreakdown?.lawyer_density ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-amber-900/30 border border-amber-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-300">High-Volume Attorney</span>
                                      </div>
                                    )}
                                    {(claim.riskBreakdown?.provider_lawyer_combo ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-orange-900/30 border border-orange-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                                        <span className="text-xs text-orange-300">Provider-Attorney Collusion</span>
                                      </div>
                                    )}
                                    {(claim.riskBreakdown?.ip_reuse ?? 0) > 0 && (
                                      <div className="flex items-center gap-2 bg-purple-900/30 border border-purple-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                                        <span className="text-xs text-purple-300">IP Address Anomaly</span>
                                      </div>
                                    )}

                                    {claim.modelDetails && claim.modelDetails.rule_adjustment >= 3 &&
                                     !claim.riskBreakdown?.police_report && !claim.riskBreakdown?.previous_claims && (
                                      <div className="flex items-center gap-2 bg-amber-900/30 border border-amber-800 rounded-md px-2.5 py-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                        <span className="text-xs text-amber-300">Legal Representation Present</span>
                                      </div>
                                    )}

                                    {(!claim.modelDetails || claim.modelDetails.model_score <= 30) &&
                                     (!claim.graphFeatures || (claim.graphFeatures.shared_doctors === 0 && claim.graphFeatures.shared_lawyers === 0 && claim.graphFeatures.shared_ips === 0)) &&
                                     (!claim.riskBreakdown || ((claim.riskBreakdown.police_report ?? 0) === 0 && (claim.riskBreakdown.previous_claims ?? 0) === 0 &&
                                     (claim.riskBreakdown.provider_volume ?? 0) === 0 && (claim.riskBreakdown.lawyer_density ?? 0) === 0 &&
                                     (claim.riskBreakdown.provider_lawyer_combo ?? 0) === 0 && (claim.riskBreakdown.ip_reuse ?? 0) === 0)) &&
                                     (!claim.modelDetails || claim.modelDetails.rule_adjustment < 3) && (
                                      <div className="col-span-2 flex items-center gap-2 bg-emerald-900/30 border border-emerald-800 rounded-md px-2.5 py-1.5">
                                        <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                                        <span className="text-xs text-emerald-300">No significant risk factors identified</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Network Analysis Summary - show graph metrics */}
                              {claim.graphFeatures && (
                                <div className="border-t border-slate-700 pt-4">
                                  <div className="flex items-center gap-2 mb-3">
                                    <Users className="h-4 w-4 text-indigo-400" />
                                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide">Network Analysis</h4>
                                  </div>
                                  <div className="grid grid-cols-3 gap-3">
                                    <div className="text-center bg-slate-800 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_doctors > 0 ? 'text-indigo-400' : 'text-slate-600'}`}>
                                        {claim.graphFeatures.shared_doctors}
                                      </div>
                                      <div className="text-[10px] text-slate-400 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-500">(via Provider)</div>
                                    </div>
                                    <div className="text-center bg-slate-800 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_lawyers > 0 ? 'text-indigo-400' : 'text-slate-600'}`}>
                                        {claim.graphFeatures.shared_lawyers}
                                      </div>
                                      <div className="text-[10px] text-slate-400 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-500">(via Attorney)</div>
                                    </div>
                                    <div className="text-center bg-slate-800 rounded-lg p-2">
                                      <div className={`text-lg font-bold ${claim.graphFeatures.shared_ips > 0 ? 'text-purple-400' : 'text-slate-600'}`}>
                                        {claim.graphFeatures.shared_ips}
                                      </div>
                                      <div className="text-[10px] text-slate-400 uppercase">Linked Claims</div>
                                      <div className="text-[9px] text-slate-500">(via IP)</div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            <div className="bg-slate-800 rounded-b-xl px-5 py-3 border-t border-slate-700">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                                  <Info className="h-3 w-3" />
                                  <span>AI-powered fraud detection analysis</span>
                                </div>
                                <div className="text-[10px] font-medium text-slate-300 uppercase tracking-wider">
                                  Confidence: High
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-slate-600 border-t-blue-500 rounded-full animate-spin" />
                          <span className="text-xs text-slate-500">Analyzing...</span>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center rounded-lg px-3 py-1.5 text-xs font-semibold ${
                        claim.status === 'settled' 
                          ? 'bg-green-900/30 text-green-400 border border-green-700/50' 
                          : claim.status === 'pending'
                          ? 'bg-amber-900/30 text-amber-400 border border-amber-700/50'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}>
                        {claim.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {claim.riskScore > 70 && (
                        <button className="rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-lg transition-all hover:shadow-xl hover:scale-105">
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
    </div>
  );
}

