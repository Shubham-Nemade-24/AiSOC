"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAlerts, triageAlert } from "@/lib/api";

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-500/10 text-red-400 border-red-500/30",
  high: "bg-orange-500/10 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",
  low: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  info: "bg-gray-500/10 text-gray-400 border-gray-500/30",
};
const VERDICT_STYLE: Record<string, string> = {
  true_positive: "bg-red-500/10 text-red-400", false_positive: "bg-green-500/10 text-green-400",
  suspicious: "bg-yellow-500/10 text-yellow-400", benign: "bg-gray-500/10 text-gray-400",
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [newCount, setNewCount] = useState(0);

  const load = () => fetchAlerts().then((data) => {
    setAlerts((prev) => {
      if (prev.length && data.length > prev.length) setNewCount(data.length - prev.length);
      return data;
    });
  }).catch(console.error).finally(() => setLoading(false));

  useEffect(() => {
    load();
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => { if (newCount > 0) { const t = setTimeout(() => setNewCount(0), 3000); return () => clearTimeout(t); } }, [newCount]);

  const handleTriage = async (id: string) => {
    setTriaging(id);
    try { await triageAlert(id); await load(); } catch (e) { console.error(e); }
    setTriaging(null);
  };

  const filtered = filter ? alerts.filter((a) => a.severity === filter) : alerts;

  if (loading) return <div className="flex items-center justify-center h-96"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Security Alerts</h1>
          <p className="text-gray-500 mt-1">{alerts.length} alerts ingested</p>
        </div>
        <div className="flex items-center gap-4">
          {newCount > 0 && (
            <div className="px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 animate-pulse">
              <span className="text-xs text-blue-400 font-medium">+{newCount} new alert{newCount > 1 ? "s" : ""}</span>
            </div>
          )}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs text-green-400 font-medium">LIVE</span>
          </div>
          <div className="flex gap-1">
            {["", "critical", "high", "medium", "low"].map((f) => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filter === f ? "bg-blue-500 text-white" : "bg-white/5 text-gray-400 hover:bg-white/10"}`}>
                {f || "All"}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-soc-card border border-soc-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-soc-border text-left">
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">Alert</th>
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">Severity</th>
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">Source</th>
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">MITRE</th>
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">AI Verdict</th>
              <th className="px-4 py-3 text-xs text-gray-500 uppercase tracking-wider font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((alert, idx) => (
              <tr key={alert.id} className={`border-b border-soc-border/50 hover:bg-white/[0.02] transition-colors ${idx < newCount ? "animate-pulse bg-blue-500/5" : ""}`}>
                <td className="px-4 py-3">
                  <Link href={`/alerts/${alert.id}`} className="text-sm font-medium text-white hover:text-blue-400 transition-colors">{alert.title}</Link>
                  <p className="text-xs text-gray-500 mt-0.5">{alert.hostname} · {alert.username}</p>
                </td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-md text-xs font-semibold border ${SEV_STYLE[alert.severity]}`}>{alert.severity}</span></td>
                <td className="px-4 py-3 text-sm text-gray-400">{alert.source}</td>
                <td className="px-4 py-3"><span className="text-xs text-gray-500">{alert.mitre_id}</span></td>
                <td className="px-4 py-3">
                  {alert.ai_verdict ? <span className={`px-2 py-1 rounded-md text-xs font-medium ${VERDICT_STYLE[alert.ai_verdict] || ""}`}>{alert.ai_verdict.replace("_", " ")}</span> : <span className="text-xs text-gray-600">—</span>}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    {!alert.ai_verdict && (
                      <button onClick={() => handleTriage(alert.id)} disabled={triaging === alert.id}
                        className="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded-md text-xs font-medium hover:bg-blue-500/20 transition-all disabled:opacity-50">
                        {triaging === alert.id ? "⏳" : "🤖"} Triage
                      </button>
                    )}
                    <Link href={`/alerts/${alert.id}`} className="px-3 py-1 bg-white/5 text-gray-400 border border-white/10 rounded-md text-xs font-medium hover:bg-white/10 transition-all">View</Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
