"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

interface ClaimData {
  id: string;
  claimantName?: string;
  policyNumber?: string;
  incidentType?: string;
  incidentDate?: string;
  description?: string;
  claimant_name?: string;
  policy_number?: string;
  loss_type?: string;
  accident_date?: string;
  accident_description?: string;
  claimant_city?: string;
  claimant_state?: string;
  vehicle_make?: string;
  vehicle_model?: string;
  lawyer_name?: string;
  medical_provider_name?: string;
}

function FormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const claimId = searchParams.get("claimId");
  const prefill = searchParams.get("prefill") === "true";

  const [claimData, setClaimData] = useState<ClaimData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch claim data if prefill is requested
    if (claimId && prefill) {
      setLoading(true);
      fetch(`http://localhost:8000/api/claims/${claimId}`)
        .then(res => res.json())
        .then(data => {
          setClaimData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching claim:", err);
          setLoading(false);
        });
    }
  }, [claimId, prefill]);

  useEffect(() => {
    // Listen for messages from the iframe (form submission success)
    const handleMessage = (event: MessageEvent) => {
      // Only accept messages from our backend
      if (event.origin !== "http://localhost:8000") return;

      if (event.data.type === "CLAIM_SUBMITTED") {
        // Notify dashboard to refresh (if open in another tab)
        window.localStorage.setItem("claimSubmitted", Date.now().toString());

        // Optionally show success message
        console.log("Claim submitted:", event.data.claimId);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  return (
    <div className="h-full overflow-auto p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-2 text-sm font-medium transition-colors"
          >
            <svg
              className="w-4 h-4"
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
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-slate-900">
            {claimData ? "Review Claim" : "Submit Insurance Claim"}
          </h1>
          {claimData && (
            <p className="text-sm text-slate-600 mt-1">
              Viewing claim for: <span className="font-semibold">{claimData.claimantName || claimData.claimant_name}</span>
            </p>
          )}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <p className="text-slate-600">Loading claim data...</p>
        </div>
      )}

      {/* Show banner when viewing existing claim */}
      {claimData && !loading && (
        <div className="bg-green-50 border-l-4 border-green-600 p-4 mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-800">
                <span className="font-semibold">Read-Only View:</span> {claimData.claimantName || claimData.claimant_name} | Policy: {claimData.policyNumber || claimData.policy_number}
              </p>
              <p className="text-xs text-green-700 mt-1">
                This claim has been submitted and cannot be modified.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Embedded Backend Form - Always show, pre-fill if data exists */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <iframe
          src={claimData 
            ? `http://localhost:8000/?prefill=${encodeURIComponent(JSON.stringify(claimData))}`
            : "http://localhost:8000/"
          }
          className="w-full border-0"
          style={{ minHeight: "1200px", height: "auto" }}
          title="Insurance Claim Submission Form"
        />
      </div>
    </div>
  );
}

export default function FormPage() {
  return (
    <Suspense fallback={<div className="p-8">Loading...</div>}>
      <FormContent />
    </Suspense>
  );
}

