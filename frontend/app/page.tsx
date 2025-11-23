"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-8">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            RiskChain Intelligence
          </h1>
          <p className="text-xl text-slate-600">
            Insurance Fraud Detection & Risk Analysis System
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Employee Portal */}
          <Link
            href="/dashboard"
            className="group bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-slate-900"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Employee Portal
              </h2>
              <p className="text-slate-600 mb-4">
                Access the dashboard to review and manage incoming claims
              </p>
              <div className="text-sm text-slate-500">
                View claims • Risk analysis • Fraud detection
              </div>
            </div>
          </Link>

          {/* Claim Submission */}
          <Link
            href="/form"
            className="group bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-slate-900"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Submit a Claim
              </h2>
              <p className="text-slate-600 mb-4">
                File a new insurance claim for processing
              </p>
              <div className="text-sm text-slate-500">
                Auto & Healthcare • Real-time risk scoring
              </div>
            </div>
          </Link>
        </div>

        <div className="mt-12 text-center text-slate-500 text-sm">
          <p>Select an option above to continue</p>
        </div>
      </div>
    </div>
  );
}
