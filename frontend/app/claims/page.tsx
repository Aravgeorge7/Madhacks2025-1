"use client";

import { Inbox } from "lucide-react";

export default function ClaimsInbox() {
  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <Inbox className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Claims Inbox</h1>
            <p className="text-slate-600 mt-1">Manage and review all insurance claims</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-professional-lg p-12 text-center">
          <Inbox className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Claims Inbox</h2>
          <p className="text-slate-600">
            This page is under development. Claims management features will be available here.
          </p>
        </div>
      </div>
    </div>
  );
}

