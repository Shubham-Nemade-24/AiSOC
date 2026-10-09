"use client";
import { useEffect, useState } from "react";
import { fetchInvestigations } from "@/lib/api";

export default function InvestigationsPage() {
  const [invs, setInvs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchInvestigations().then(setInvs).catch(console.error).finally(() => setLoading(false)); }, []);

  if (loading) return <div className="flex items-center justify-center h-[80vh]"><div className="w-10 h-10 rounded-full border-2 border-purple-500/20 border-t-purple-500 animate-spin" /></div>;

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="animate-slide-up">
        <p className="text-purple-400/60 text-xs font-semibold uppercase tracking-[0.2em] mb-1">AI Analysis</p>
        <h1 className="text-4xl font-extrabold text-white tracking-tight">Investigations</h1>
        <p className="text-slate-500 text-sm mt-1">{invs.length} multi-agent investigation{invs.length !== 1 ? "s" : ""} completed</p>
      </div>

      {invs.length === 0 ? (
        <div className="glass rounded-2xl p-12 text-center animate-slide-up">
          <p className="text-5xl mb-4">🔍</p>
          <p className="text-lg font-semibold text-slate-300">No investigations yet</p>
          <p className="text-sm text-slate-500 mt-2">Go to an alert and click "Full AI Investigation" to run the multi-agent pipeline</p>
        </div>
      ) : (
        <div className="space-y-4">
          {invs.map((inv: any, i: number) => (
            <div key={inv.id} className="glass glass-hover rounded-2xl p-6 animate-slide-up" style={{animationDelay: `${i*80}ms`}}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-violet-600/10 flex items-center justify-center text-lg border border-purple-500/15">🔬</div>
                  <div>
                    <p className="text-[13px] font-bold text-white">Investigation #{i + 1}</p>
                    <p className="text-[11px] text-slate-500 font-mono mt-0.5">Alert: {inv.alert_id?.substring(0, 8)}…</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {inv.risk_score && (
                    <div className={`px-3 py-1.5 rounded-lg text-xs font-bold ${inv.risk_score >= 7 ? "bg-red-500/10 text-red-400 border border-red-500/15" : inv.risk_score >= 4 ? "bg-amber-500/10 text-amber-400 border border-amber-500/15" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/15"}`}>
                      Risk: {inv.risk_score}/10
                    </div>
                  )}
                  <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg text-[11px] font-bold">{inv.status}</span>
                </div>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed bg-white/[0.02] rounded-xl p-4 border border-white/[0.03]">{inv.summary || "No summary available"}</p>
              {inv.ledger_entries && (
                <div className="flex items-center gap-2 mt-3 text-[10px] text-slate-600">
                  <span>📋 {inv.ledger_entries.length || 0} ledger entries</span>
                  <span>·</span>
                  <span>🔗 SHA-256 hash chain</span>
                  <span>·</span>
                  <span>🔒 Pseudonymized</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
