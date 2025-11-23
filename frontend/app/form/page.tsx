"use client";

import Link from "next/link";

export default function FormPage() {
  return (
    <div className="h-full overflow-auto p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            href="/"
            className="text-slate-600 hover:text-slate-900 mb-2 inline-block"
          >
            ← Back to Dashboard
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

