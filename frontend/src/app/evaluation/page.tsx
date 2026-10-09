"use client";
import { useEffect, useState } from "react";

export default function EvaluationPage() {
  const [data, setData] = useState<any>(null);
  const [corr, setCorr] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/dashboard/evaluation").then(r => r.json()),
      fetch("/api/dashboard/correlations").then(r => r.json()),
    ]).then(([e, c]) => { setData(e); setCorr(c); }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-[80vh]"><div className="w-10 h-10 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" /></div>;
  if (!data) return <div className="glass rounded-2xl p-8 text-center"><p className="text-red-400">Failed to load</p></div>;

  const t = data.triage_metrics, inv = data.investigation_metrics, ledger = data.ledger_integrity;

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="animate-slide-up">
        <p className="text-blue-400/60 text-xs font-semibold uppercase tracking-[0.2em] mb-1">Performance Analysis</p>
        <h1 className="text-4xl font-extrabold text-white tracking-tight">Evaluation Harness</h1>
        <p className="text-slate-500 text-sm mt-1">System metrics, triage accuracy & audit integrity</p>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-4 gap-4 animate-slide-up" style={{animationDelay:"80ms"}}>
        {[
          { label: "Triage Rate", value: `${t.triage_rate_pct}%`, sub: `${t.triaged}/${t.total_alerts}`, icon: "🎯", color: "blue" },
          { label: "Alert Reduction", value: `${t.alert_reduction_rate_pct}%`, sub: "noise filtered", icon: "📉", color: "emerald" },
          { label: "Avg Confidence", value: `${(t.avg_confidence * 100).toFixed(0)}%`, sub: "model certainty", icon: "🧠", color: "purple" },
          { label: "Hash Coverage", value: `${ledger.hash_coverage_pct}%`, sub: `${ledger.hashed_entries} entries`, icon: "🔗", color: "cyan" },
        ].map((c, i) => {
          const grd = { blue: "from-blue-500/10", emerald: "from-emerald-500/10", purple: "from-purple-500/10", cyan: "from-cyan-500/10" }[c.color];
          const brd = { blue: "border-blue-500/15", emerald: "border-emerald-500/15", purple: "border-purple-500/15", cyan: "border-cyan-500/15" }[c.color];
          return (
            <div key={i} className={`glass glass-hover rounded-2xl p-5 bg-gradient-to-br ${grd} to-transparent ${brd}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] text-slate-500 uppercase tracking-[0.15em] font-bold">{c.label}</p>
                  <p className="text-3xl font-extrabold text-white mt-2">{c.value}</p>
                  <p className="text-[10px] text-slate-500 mt-1">{c.sub}</p>
                </div>
                <span className="text-2xl opacity-40">{c.icon}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Verdict Breakdown */}
      <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"160ms"}}>
        <h3 className="text-[11px] font-bold text-blue-400/80 uppercase tracking-[0.15em] mb-5">🤖 Verdict Distribution</h3>
        <div className="grid grid-cols-4 gap-4 mb-5">
          {[
            { k: "true_positive", label: "True Positive", color: "red", desc: "Confirmed threats" },
            { k: "false_positive", label: "False Positive", color: "emerald", desc: "Noise eliminated" },
            { k: "suspicious", label: "Suspicious", color: "amber", desc: "Needs review" },
            { k: "benign", label: "Benign", color: "slate", desc: "Safe activity" },
          ].map((v) => {
            const bg = { red: "from-red-500/15", emerald: "from-emerald-500/15", amber: "from-amber-500/15", slate: "from-slate-500/15" }[v.color];
            const txt = { red: "text-red-400", emerald: "text-emerald-400", amber: "text-amber-400", slate: "text-slate-400" }[v.color];
            const count = t.verdicts[v.k] || 0;
            const pct = t.triaged > 0 ? ((count / t.triaged) * 100).toFixed(0) : 0;
            return (
              <div key={v.k} className={`rounded-xl p-5 bg-gradient-to-br ${bg} to-transparent border border-white/[0.04]`}>
                <p className={`text-3xl font-extrabold ${txt}`}>{count}</p>
                <p className="text-[10px] text-slate-500 uppercase font-bold mt-1 tracking-wider">{v.label}</p>
                <div className="mt-3 w-full h-1 rounded-full bg-white/[0.05]">
                  <div className={`h-full rounded-full ${txt} bg-current opacity-40`} style={{width: `${pct}%`}} />
                </div>
                <p className="text-[10px] text-slate-600 mt-1">{pct}% · {v.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Investigation + Ledger */}
      <div className="grid grid-cols-2 gap-5">
        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"240ms"}}>
          <h3 className="text-[11px] font-bold text-purple-400/80 uppercase tracking-[0.15em] mb-5">🔍 Investigation Pipeline</h3>
          <div className="space-y-4">
            {[
              ["Total Pipelines", inv.total_investigations, "multi-agent runs"],
              ["Completed", inv.completed, `${inv.completion_rate_pct}% rate`],
              ["Avg Risk Score", `${inv.avg_risk_score}/10`, "threat assessment"],
            ].map(([l, v, s]) => (
              <div key={l as string} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/[0.03]">
                <div><p className="text-[12px] text-slate-300 font-semibold">{l}</p><p className="text-[10px] text-slate-600">{s}</p></div>
                <p className="text-xl font-extrabold text-white">{v}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"320ms"}}>
          <h3 className="text-[11px] font-bold text-emerald-400/80 uppercase tracking-[0.15em] mb-5">🔒 Ledger Integrity</h3>
          <div className="space-y-4">
            {[
              ["Total Entries", ledger.total_entries, "audit records"],
              ["SHA-256 Hashed", ledger.hashed_entries, `${ledger.hash_coverage_pct}% coverage`],
              ["Pseudonymized", ledger.pseudonymized_entries, "privacy-protected"],
            ].map(([l, v, s]) => (
              <div key={l as string} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/[0.03]">
                <div><p className="text-[12px] text-slate-300 font-semibold">{l}</p><p className="text-[10px] text-slate-600">{s}</p></div>
                <p className="text-xl font-extrabold text-white">{v}</p>
              </div>
            ))}
          </div>
          {ledger.hash_coverage_pct === 100 && ledger.total_entries > 0 && (
            <div className="mt-4 px-4 py-2.5 bg-emerald-500/[0.08] border border-emerald-500/15 rounded-xl">
              <p className="text-[12px] text-emerald-400 font-semibold">✓ Hash chain intact — all entries verified</p>
            </div>
          )}
        </div>
      </div>

      {/* Correlations */}
      <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"400ms"}}>
        <h3 className="text-[11px] font-bold text-cyan-400/80 uppercase tracking-[0.15em] mb-5">🔗 Alert Correlations</h3>
        {corr?.total_groups > 0 ? (
          <div className="space-y-3">
            {corr.correlations.map((g: any, i: number) => {
              const sevColor = { critical: "bg-red-500/10 text-red-400 border-red-500/20", high: "bg-orange-500/10 text-orange-400 border-orange-500/20", medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" }[g.max_severity] || "bg-slate-500/10 text-slate-400 border-slate-500/20";
              return (
                <div key={i} className="glass-hover rounded-xl p-5 border border-white/[0.04] bg-white/[0.01]">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-sm font-extrabold">{g.alert_count}</span>
                      <span className="text-[13px] font-bold text-white">Correlated Group {i + 1}</span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border ${sevColor}`}>{g.max_severity}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {g.shared_entities.slice(0, 8).map((e: string, j: number) => (
                      <span key={j} className="px-2 py-0.5 bg-blue-500/[0.08] text-blue-400/80 border border-blue-500/10 rounded-md text-[10px] font-mono">{e}</span>
                    ))}
                  </div>
                  <div className="text-[11px] text-slate-500 mb-2">Tactics: <span className="text-slate-400">{g.mitre_tactics.join(", ")}</span> · <span className="text-slate-400">{g.time_span_minutes}min span</span></div>
                  <div className="space-y-0.5">
                    {g.alert_titles.slice(0, 3).map((t: string, j: number) => (
                      <p key={j} className="text-[11px] text-slate-400">• {t}</p>
                    ))}
                    {g.alert_titles.length > 3 && <p className="text-[10px] text-slate-600">+{g.alert_titles.length - 3} more alerts</p>}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8"><p className="text-slate-600 text-sm">No correlated groups yet</p><p className="text-slate-700 text-xs mt-1">Correlations form when alerts share entities within a 60-minute window</p></div>
        )}
      </div>
    </div>
  );
}
