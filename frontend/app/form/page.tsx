"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function FormPage() {
  const router = useRouter();

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
            href="/"
            className="text-slate-600 hover:text-slate-900 mb-2 inline-block text-sm"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl font-bold text-slate-900">
            Submit Insurance Claim
          </h1>
        </div>
      </div>
      
      {/* Embedded Backend Form - Connected to Database */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <iframe
          src="http://localhost:8000/"
          className="w-full border-0"
          style={{ minHeight: "1200px", height: "auto" }}
          title="Insurance Claim Submission Form"
        />
      </div>
    </div>
  );
}

