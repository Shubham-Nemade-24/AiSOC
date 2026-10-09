"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchAlert, triageAlert, investigateAlert } from "@/lib/api";

export default function AlertDetailPage() {
  const { id } = useParams();
  const [alert, setAlert] = useState<any>(null);
  const [investigation, setInvestigation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState(false);
  const [investigating, setInvestigating] = useState(false);

  useEffect(() => { if (id) fetchAlert(id as string).then(setAlert).finally(() => setLoading(false)); }, [id]);

  const handleTriage = async () => {
    setTriaging(true);
    try { await triageAlert(id as string); setAlert(await fetchAlert(id as string)); } catch(e) { console.error(e); }
    setTriaging(false);
  };
  const handleInvestigate = async () => {
    setInvestigating(true);
    try { const inv = await investigateAlert(id as string); setInvestigation(inv); setAlert(await fetchAlert(id as string)); } catch(e) { console.error(e); }
    setInvestigating(false);
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!alert) return <p className="text-red-400">Alert not found</p>;

  const sevColor: Record<string, string> = { critical: "text-red-400 bg-red-500/10 border-red-500/30", high: "text-orange-400 bg-orange-500/10 border-orange-500/30", medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30", low: "text-blue-400 bg-blue-500/10 border-blue-500/30", info: "text-gray-400 bg-gray-500/10 border-gray-500/30" };

  return (
    <div className="space-y-6 max-w-5xl">
      <Link href="/alerts" className="text-sm text-gray-500 hover:text-blue-400 transition-colors">← Back to Alerts</Link>

      {/* Header */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-2 py-1 rounded-md text-xs font-semibold border ${sevColor[alert.severity]}`}>{alert.severity}</span>
              <span className="text-xs text-gray-500">{alert.source} · {alert.mitre_id}</span>
              {alert.ocsf_class_uid && <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 rounded text-[10px] font-mono">OCSF:{alert.ocsf_class_uid}</span>}
            </div>
            <h1 className="text-2xl font-bold text-white">{alert.title}</h1>
            <p className="text-gray-400 mt-2 text-sm leading-relaxed">{alert.description}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-soc-border">
          {[["Source IP", alert.source_ip], ["Dest IP", alert.dest_ip], ["Hostname", alert.hostname], ["Username", alert.username],
            ["MITRE Tactic", alert.mitre_tactic], ["MITRE Technique", alert.mitre_technique], ["Status", alert.status], ["Created", new Date(alert.created_at).toLocaleString()]
          ].map(([label, value]) => (
            <div key={label as string}><p className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</p><p className="text-sm text-white mt-0.5 font-mono">{value || "N/A"}</p></div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={handleTriage} disabled={triaging || !!alert.ai_verdict}
          className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg text-sm font-semibold hover:from-blue-500 hover:to-blue-400 transition-all disabled:opacity-40 shadow-lg shadow-blue-500/20">
          {triaging ? "⏳ Triaging..." : alert.ai_verdict ? "✓ Triaged" : "🤖 AI Triage"}
        </button>
        <button onClick={handleInvestigate} disabled={investigating}
          className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg text-sm font-semibold hover:from-purple-500 hover:to-purple-400 transition-all disabled:opacity-40 shadow-lg shadow-purple-500/20">
          {investigating ? "⏳ Investigating..." : "🔍 AI Investigation"}
        </button>
      </div>

      {/* AI Triage */}
      {alert.ai_verdict && (
        <div className="bg-soc-card border border-soc-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">🤖 AI Triage Result</h3>
            <span className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded text-[10px]">🔒 Pseudonymized</span>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="p-3 rounded-lg bg-white/5"><p className="text-[10px] text-gray-500 uppercase">Verdict</p><p className="text-lg font-bold text-white mt-1">{alert.ai_verdict.replace("_", " ")}</p></div>
            <div className="p-3 rounded-lg bg-white/5"><p className="text-[10px] text-gray-500 uppercase">Confidence</p><p className="text-lg font-bold text-white mt-1">{(alert.ai_confidence * 100).toFixed(0)}%</p></div>
            <div className="p-3 rounded-lg bg-white/5"><p className="text-[10px] text-gray-500 uppercase">Priority</p><p className="text-lg font-bold text-white mt-1">{alert.ai_priority}/10</p></div>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed bg-white/5 rounded-lg p-4">{alert.ai_reasoning}</p>
        </div>
      )}

      {/* Investigation with Ledger Hash Chain */}
      {investigation && (
        <div className="bg-soc-card border border-soc-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">🔍 Investigation Report</h3>
            <span className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded text-[10px]">🔒 SHA-256 Verified</span>
          </div>
          <div className="flex items-center gap-4 mb-4">
            <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded text-xs font-medium">{investigation.status}</span>
            {investigation.risk_score && <span className="text-sm text-gray-400">Risk: <strong className="text-white">{investigation.risk_score}/10</strong></span>}
          </div>
          <p className="text-sm text-gray-300 bg-white/5 rounded-lg p-4 mb-6 leading-relaxed">{investigation.summary}</p>

          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Investigation Ledger — Immutable Hash Chain</h4>
          <div className="space-y-3">
            {investigation.ledger?.map((entry: any, i: number) => (
              <div key={i} className="border border-soc-border rounded-lg p-4 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs flex items-center justify-center font-bold">{entry.step}</span>
                    <span className="text-sm font-semibold text-white">{entry.agent.replace(/_/g, " ")}</span>
                    <span className="text-xs text-gray-500">· {entry.action}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    {entry.pseudonymized && <span className="px-1.5 py-0.5 bg-green-500/10 text-green-400 rounded text-[10px]">🔒</span>}
                    <span>🧠 {entry.model}</span>
                    {entry.tokens && <span>{entry.tokens}tok</span>}
                    {entry.duration_ms && <span>{entry.duration_ms}ms</span>}
                  </div>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">{entry.output}</p>
                {entry.content_hash && (
                  <div className="mt-2 pt-2 border-t border-soc-border/50 flex items-center gap-2">
                    <span className="text-[10px] text-gray-600 font-mono">SHA-256: {entry.content_hash.substring(0, 16)}...</span>
                    {entry.prev_hash && <span className="text-[10px] text-gray-600 font-mono">← {entry.prev_hash.substring(0, 8)}...</span>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
