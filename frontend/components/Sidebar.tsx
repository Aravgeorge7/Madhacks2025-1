"use client";

import { LayoutDashboard, Inbox, Network, BarChart } from "lucide-react";
import Link from "next/link";

export default function Sidebar() {
  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard, href: "/" },
    { name: "Claims Inbox", icon: Inbox, href: "/claims" },
    { name: "Risk Graph", icon: Network, href: "/graph" },
    { name: "Analytics", icon: BarChart, href: "/analytics" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900">
      <div className="flex h-full flex-col p-6">
        <h1 className="mb-8 text-2xl font-bold text-white">RiskChain</h1>
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center gap-3 rounded-lg px-4 py-3 text-gray-300 transition-colors hover:bg-slate-800 hover:text-white"
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}

