"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAlerts, triageAlert } from "@/lib/api";

const SEV: Record<string, { bg: string; text: string; dot: string }> = {
  critical: { bg: "bg-red-500/10 border-red-500/20", text: "text-red-400", dot: "bg-red-400" },
  high: { bg: "bg-orange-500/10 border-orange-500/20", text: "text-orange-400", dot: "bg-orange-400" },
  medium: { bg: "bg-yellow-500/10 border-yellow-500/20", text: "text-yellow-400", dot: "bg-yellow-400" },
  low: { bg: "bg-blue-500/10 border-blue-500/20", text: "text-blue-400", dot: "bg-blue-400" },
  info: { bg: "bg-slate-500/10 border-slate-500/20", text: "text-slate-400", dot: "bg-slate-400" },
};
const VERDICT: Record<string, string> = { true_positive: "text-red-400 bg-red-500/10", false_positive: "text-emerald-400 bg-emerald-500/10", suspicious: "text-yellow-400 bg-yellow-500/10", benign: "text-slate-400 bg-slate-500/10" };

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [newCount, setNewCount] = useState(0);

  const load = () => fetchAlerts().then((d) => {
    setAlerts((prev) => { if (prev.length && d.length > prev.length) setNewCount(d.length - prev.length); return d; });
  }).catch(console.error).finally(() => setLoading(false));

  useEffect(() => { load(); const i = setInterval(load, 8000); return () => clearInterval(i); }, []);
  useEffect(() => { if (newCount > 0) { const t = setTimeout(() => setNewCount(0), 3000); return () => clearTimeout(t); } }, [newCount]);

  const handleTriage = async (id: string) => { setTriaging(id); try { await triageAlert(id); await load(); } catch(e) {} setTriaging(null); };
  const filtered = filter ? alerts.filter((a) => a.severity === filter) : alerts;

  if (loading) return <div className="flex items-center justify-center h-[80vh]"><div className="w-10 h-10 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between animate-slide-up">
        <div>
          <p className="text-blue-400/60 text-xs font-semibold uppercase tracking-[0.2em] mb-1">Alert Management</p>
          <h1 className="text-4xl font-extrabold text-white tracking-tight">Security Alerts</h1>
          <p className="text-slate-500 text-sm mt-1">{alerts.length} total events ingested</p>
        </div>
        <div className="flex items-center gap-3">
          {newCount > 0 && (
            <div className="px-3 py-1.5 glass rounded-full border-blue-500/30 animate-pulse">
              <span className="text-xs text-blue-400 font-semibold">+{newCount} new</span>
            </div>
          )}
          <div className="flex items-center gap-2 px-3 py-1.5 glass rounded-full">
            <div className="relative"><span className="w-2 h-2 rounded-full bg-emerald-400 block" /><span className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-75" /></div>
            <span className="text-[11px] text-emerald-400 font-semibold">LIVE</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-1.5 animate-slide-up" style={{animationDelay:"80ms"}}>
        {["", "critical", "high", "medium", "low", "info"].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all duration-300 ${filter === f ? "bg-blue-500 text-white shadow-lg shadow-blue-500/25" : "glass text-slate-400 hover:text-white hover:bg-white/[0.06]"}`}>
            {f ? f.charAt(0).toUpperCase() + f.slice(1) : "All"}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="glass rounded-2xl overflow-hidden animate-slide-up" style={{animationDelay:"160ms"}}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead><tr className="border-b border-white/[0.06]">
              {["Alert", "Severity", "Source", "MITRE", "AI Verdict", "Actions"].map((h) => (
                <th key={h} className="px-5 py-3.5 text-left text-[10px] text-slate-500 uppercase tracking-[0.15em] font-bold">{h}</th>
              ))}
            </tr></thead>
            <tbody>
              {filtered.map((alert, idx) => (
                <tr key={alert.id} className={`border-b border-white/[0.03] hover:bg-white/[0.02] transition-all duration-200 group ${idx < newCount ? "bg-blue-500/[0.03]" : ""}`}>
                  <td className="px-5 py-3.5">
                    <Link href={`/alerts/${alert.id}`} className="text-[13px] font-semibold text-slate-200 group-hover:text-blue-400 transition-colors line-clamp-1">{alert.title}</Link>
                    <p className="text-[11px] text-slate-600 mt-0.5 font-mono">{alert.hostname} · {alert.username}</p>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold border ${SEV[alert.severity]?.bg} ${SEV[alert.severity]?.text}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${SEV[alert.severity]?.dot}`} />{alert.severity}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-[12px] text-slate-400 font-medium">{alert.source}</td>
                  <td className="px-5 py-3.5"><span className="text-[11px] text-slate-500 font-mono bg-white/[0.03] px-2 py-0.5 rounded">{alert.mitre_id}</span></td>
                  <td className="px-5 py-3.5">
                    {alert.ai_verdict ? <span className={`px-2.5 py-1 rounded-lg text-[11px] font-bold ${VERDICT[alert.ai_verdict]}`}>{alert.ai_verdict.replace("_"," ")}</span> : <span className="text-slate-700 text-xs">—</span>}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex gap-2">
                      {!alert.ai_verdict && (
                        <button onClick={() => handleTriage(alert.id)} disabled={triaging === alert.id}
                          className="px-3 py-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg text-[11px] font-semibold hover:bg-blue-500/20 transition-all disabled:opacity-40">
                          {triaging === alert.id ? "⏳" : "🤖"} Triage
                        </button>
                      )}
                      <Link href={`/alerts/${alert.id}`} className="px-3 py-1.5 glass rounded-lg text-[11px] text-slate-400 font-medium hover:text-white transition-all">View →</Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
