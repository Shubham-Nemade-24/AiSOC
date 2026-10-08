"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchInvestigations } from "@/lib/api";

export default function InvestigationsPage() {
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvestigations().then(setInvestigations).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-96"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">AI Investigations</h1>
        <p className="text-gray-500 mt-1">Autonomous multi-agent investigation pipeline results</p>
      </div>

      {investigations.length === 0 ? (
        <div className="bg-soc-card border border-soc-border rounded-xl p-12 text-center">
          <p className="text-4xl mb-3">🔍</p>
          <p className="text-gray-400">No investigations yet</p>
          <p className="text-sm text-gray-500 mt-1">Go to an alert and click "AI Investigation" to start one</p>
          <Link href="/alerts" className="inline-block mt-4 px-4 py-2 bg-blue-500/10 text-blue-400 rounded-lg text-sm hover:bg-blue-500/20 transition-all">
            View Alerts →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {investigations.map((inv) => {
            const sevColor: Record<string, string> = { critical: "border-red-500/30 bg-red-500/5", high: "border-orange-500/30 bg-orange-500/5", medium: "border-yellow-500/30 bg-yellow-500/5", low: "border-blue-500/30 bg-blue-500/5" };
            return (
              <Link key={inv.id} href={`/alerts/${inv.alert_id}`}
                className={`block bg-soc-card border rounded-xl p-5 hover:bg-white/[0.02] transition-all ${sevColor[inv.alert_severity] || "border-soc-border"}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-semibold">{inv.alert_title}</h3>
                    <p className="text-sm text-gray-400 mt-1 line-clamp-2">{inv.summary?.substring(0, 200)}</p>
                  </div>
                  <div className="text-right flex-shrink-0 ml-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${inv.status === "completed" ? "bg-green-500/10 text-green-400" : "bg-yellow-500/10 text-yellow-400"}`}>
                      {inv.status}
                    </span>
                    {inv.risk_score && <p className="text-sm text-gray-500 mt-2">Risk: <strong className="text-white">{inv.risk_score}/10</strong></p>}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
