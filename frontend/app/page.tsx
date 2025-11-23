"use client";

import Link from "next/link";
import { Shield, FileText, ArrowRight, CheckCircle2, BarChart3, Network, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-8 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000" />
      </div>

      <div className="max-w-5xl w-full relative z-10 animate-fade-in">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-professional-lg mb-6">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-6xl font-bold text-white mb-4 tracking-tight">
            RiskChain Intelligence
          </h1>
          <p className="text-xl text-slate-400 font-medium max-w-2xl mx-auto">
            Advanced Insurance Fraud Detection & Risk Analysis System
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-sm text-slate-500">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>Real-Time Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>Graph Network Detection</span>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <Link
            href="/login"
            className="group relative bg-slate-900 rounded-2xl shadow-professional-lg p-8 hover:shadow-professional-xl transition-all duration-300 border border-slate-800 hover:border-blue-600 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-indigo-500/0 group-hover:from-blue-500/10 group-hover:to-indigo-500/10 transition-all duration-300" />
            
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
              </div>
              
              <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-400 transition-colors">
                Employee Portal
              </h2>
              <p className="text-slate-400 mb-6 leading-relaxed">
                Employee access only. Review, analyze, and manage incoming insurance claims with advanced risk assessment and fraud detection tools.
              </p>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
                  <span>View & manage claims</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
                  <span>AI-powered risk analysis</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-purple-500 rounded-full" />
                  <span>Fraud detection & network graphs</span>
                </div>
              </div>
            </div>
          </Link>

          <Link
            href="/form"
            className="group relative bg-slate-900 rounded-2xl shadow-professional-lg p-8 hover:shadow-professional-xl transition-all duration-300 border border-slate-800 hover:border-indigo-600 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 to-purple-500/0 group-hover:from-indigo-500/10 group-hover:to-purple-500/10 transition-all duration-300" />
            
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
              </div>
              
              <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-indigo-400 transition-colors">
                Submit a Claim
              </h2>
              <p className="text-slate-400 mb-6 leading-relaxed">
                File a new insurance claim with our easy-to-use submission form. Complete your claim information and our team will review it promptly.
              </p>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
                  <span>Auto & Healthcare claims</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-purple-500 rounded-full" />
                  <span>Simple step-by-step process</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-1.5 h-1.5 bg-pink-500 rounded-full" />
                  <span>Secure submission</span>
                </div>
              </div>
            </div>
          </Link>
        </div>

        <div className="bg-slate-900 rounded-2xl shadow-professional p-6 border border-slate-800">
          <div className="grid grid-cols-3 gap-6 text-center">
            <div>
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-900/50 rounded-lg mb-3">
                <Zap className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-1">Real-Time</h3>
              <p className="text-xs text-slate-400">Instant analysis</p>
            </div>
            <div>
              <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-900/50 rounded-lg mb-3">
                <Network className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="font-semibold text-white mb-1">Network Graph</h3>
              <p className="text-xs text-slate-400">Fraud ring detection</p>
            </div>
            <div>
              <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-900/50 rounded-lg mb-3">
                <Shield className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold text-white mb-1">AI-Powered</h3>
              <p className="text-xs text-slate-400">Machine learning</p>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
