import RiskNetworkGraph from "@/components/RiskNetworkGraph";

export default function GraphPage() {
  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-8 py-6">
        <h1 className="text-3xl font-bold text-slate-900">
          Fraud Network Analysis
        </h1>
        <div className="flex items-center gap-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full bg-red-500"></div>
            <span className="text-sm text-slate-700">High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full bg-blue-500"></div>
            <span className="text-sm text-slate-700">Shared Provider</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full bg-gray-500"></div>
            <span className="text-sm text-slate-700">IP</span>
          </div>
        </div>
      </div>
      <div className="flex-1" style={{ height: "calc(100vh - 120px)", minHeight: 0 }}>
        <RiskNetworkGraph />
      </div>
    </div>
  );
}

