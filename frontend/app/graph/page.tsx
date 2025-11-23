import RiskNetworkGraph3D from "@/components/RiskNetworkGraph3D";
import Link from "next/link";

export default function GraphPage() {
  return (
    <div className="flex h-screen flex-col bg-black">
      <div className="flex items-center justify-between border-b border-slate-800 bg-black/90 backdrop-blur-md px-8 py-4">
        <div>
          <Link
            href="/"
            className="text-slate-400 hover:text-cyan-400 mb-1 inline-block text-sm transition-colors"
          >
            Back to Home
          </Link>
          <h1 className="text-2xl font-semibold text-white">
            Fraud Network Analysis
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            3D visualization of claim connections
          </p>
        </div>
      </div>
      <div className="flex-1" style={{ height: "calc(100vh - 80px)", minHeight: 0 }}>
        <RiskNetworkGraph3D />
      </div>
    </div>
  );
}

