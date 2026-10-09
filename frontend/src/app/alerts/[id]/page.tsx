"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchAlert, triageAlert, investigateAlert } from "@/lib/api";

const SEV_STYLE: Record<string,string> = { critical:"bg-red-500/10 text-red-400 border-red-500/20", high:"bg-orange-500/10 text-orange-400 border-orange-500/20", medium:"bg-yellow-500/10 text-yellow-400 border-yellow-500/20", low:"bg-blue-500/10 text-blue-400 border-blue-500/20", info:"bg-slate-500/10 text-slate-400 border-slate-500/20" };
const AGENT_ICONS: Record<string,string> = { triage_agent:"🎯", enrichment_agent:"🔎", forensic_agent:"🧬", response_agent:"🛡️" };
const AGENT_COLORS: Record<string,string> = { triage_agent:"from-blue-500/20 to-blue-600/10 border-blue-500/20", enrichment_agent:"from-cyan-500/20 to-cyan-600/10 border-cyan-500/20", forensic_agent:"from-purple-500/20 to-purple-600/10 border-purple-500/20", response_agent:"from-emerald-500/20 to-emerald-600/10 border-emerald-500/20" };

export default function AlertDetail() {
  const { id } = useParams();
  const [alert, setAlert] = useState<any>(null);
  const [investigation, setInvestigation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState(false);
  const [investigating, setInvestigating] = useState(false);

  useEffect(() => { if (id) fetchAlert(id as string).then(setAlert).finally(() => setLoading(false)); }, [id]);

  const handleTriage = async () => { setTriaging(true); try { await triageAlert(id as string); setAlert(await fetchAlert(id as string)); } catch(e){} setTriaging(false); };
  const handleInvestigate = async () => { setInvestigating(true); try { const inv = await investigateAlert(id as string); setInvestigation(inv); setAlert(await fetchAlert(id as string)); } catch(e){} setInvestigating(false); };

  if (loading) return <div className="flex items-center justify-center h-[80vh]"><div className="w-10 h-10 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" /></div>;
  if (!alert) return <div className="glass rounded-2xl p-8 text-center"><p className="text-red-400">Alert not found</p></div>;

  return (
    <div className="space-y-5 max-w-5xl">
      <Link href="/alerts" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-blue-400 transition-colors font-medium">
        <span>←</span> Back to Alerts
      </Link>

      {/* Header Card */}
      <div className="glass rounded-2xl p-6 animate-slide-up">
        <div className="flex items-center gap-3 mb-3">
          <span className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border ${SEV_STYLE[alert.severity]}`}>{alert.severity.toUpperCase()}</span>
          <span className="text-xs text-slate-500 font-medium">{alert.source}</span>
          <span className="text-xs text-slate-600 font-mono bg-white/[0.03] px-2 py-0.5 rounded">{alert.mitre_id}</span>
          {alert.ocsf_class_uid && <span className="text-[10px] text-cyan-400/60 font-mono bg-cyan-500/[0.06] px-2 py-0.5 rounded">OCSF:{alert.ocsf_class_uid}</span>}
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">{alert.title}</h1>
        <p className="text-slate-400 mt-3 text-sm leading-relaxed">{alert.description}</p>

        <div className="grid grid-cols-4 gap-4 mt-6 pt-5 border-t border-white/[0.05]">
          {[["Source IP", alert.source_ip], ["Dest IP", alert.dest_ip], ["Hostname", alert.hostname], ["Username", alert.username],
            ["MITRE Tactic", alert.mitre_tactic], ["Technique", alert.mitre_technique], ["Status", alert.status], ["Created", new Date(alert.created_at).toLocaleString()]
          ].map(([l,v]) => (
            <div key={l as string}><p className="text-[9px] text-slate-600 uppercase tracking-[0.15em] font-semibold">{l}</p><p className="text-[13px] text-slate-200 mt-0.5 font-mono">{v || "—"}</p></div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 animate-slide-up" style={{animationDelay:"80ms"}}>
        <button onClick={handleTriage} disabled={triaging || !!alert.ai_verdict}
          className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 disabled:opacity-30 disabled:hover:shadow-none">
          {triaging ? "⏳ Analyzing..." : alert.ai_verdict ? "✓ Triaged" : "🤖 AI Triage"}
        </button>
        <button onClick={handleInvestigate} disabled={investigating}
          className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-violet-500 text-white rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300 disabled:opacity-30">
          {investigating ? "⏳ Running Pipeline..." : "🔍 Full AI Investigation"}
        </button>
      </div>

      {/* Triage Result */}
      {alert.ai_verdict && (
        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"160ms"}}>
          <div className="flex items-center gap-2.5 mb-5">
            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.15em]">AI Triage Result</h3>
            <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-md text-[10px] font-semibold">🔒 Pseudonymized</span>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-5">
            {[["Verdict", alert.ai_verdict.replace("_"," "), "text-white"], ["Confidence", `${(alert.ai_confidence*100).toFixed(0)}%`, "text-blue-400"], ["Priority", `${alert.ai_priority}/10`, "text-amber-400"]].map(([l,v,c]) => (
              <div key={l} className="glass rounded-xl p-4"><p className="text-[9px] text-slate-600 uppercase tracking-wider font-semibold">{l}</p><p className={`text-xl font-extrabold mt-1 ${c}`}>{v}</p></div>
            ))}
          </div>
          <div className="bg-white/[0.02] rounded-xl p-4 border border-white/[0.04]">
            <p className="text-sm text-slate-300 leading-relaxed">{alert.ai_reasoning}</p>
          </div>
        </div>
      )}

      {/* Investigation */}
      {investigation && (
        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"240ms"}}>
          <div className="flex items-center gap-2.5 mb-2">
            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.15em]">Multi-Agent Investigation</h3>
            <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-md text-[10px] font-semibold">🔗 SHA-256 Chain</span>
          </div>
          <div className="flex items-center gap-4 mb-5">
            <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg text-xs font-bold">{investigation.status}</span>
            {investigation.risk_score && <span className="text-sm text-slate-400">Risk: <strong className="text-white">{investigation.risk_score}/10</strong></span>}
          </div>
          <div className="bg-white/[0.02] rounded-xl p-4 border border-white/[0.04] mb-6">
            <p className="text-sm text-slate-300 leading-relaxed">{investigation.summary}</p>
          </div>

          <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em] mb-4">Investigation Ledger — Immutable Hash Chain</h4>
          <div className="space-y-3">
            {investigation.ledger?.map((e: any, i: number) => (
              <div key={i} className={`rounded-xl p-5 bg-gradient-to-br ${AGENT_COLORS[e.agent] || "from-slate-500/10 to-transparent"} border border-white/[0.05] animate-slide-up`} style={{animationDelay:`${i*100}ms`}}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xl">{AGENT_ICONS[e.agent] || "🔧"}</span>
                    <div>
                      <span className="text-[13px] font-bold text-white">{e.agent.replace(/_/g," ").replace(/\b\w/g, (c:string) => c.toUpperCase())}</span>
                      <span className="text-[11px] text-slate-500 ml-2">· {e.action}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-slate-600">
                    {e.pseudonymized && <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-[9px] font-semibold">🔒 Private</span>}
                    <span className="font-mono">{e.model}</span>
                    {e.tokens && <span>{e.tokens} tok</span>}
                    {e.duration_ms && <span>{e.duration_ms}ms</span>}
                  </div>
                </div>
                <p className="text-[13px] text-slate-300 leading-relaxed">{e.output}</p>
                {e.content_hash && (
                  <div className="mt-3 pt-2.5 border-t border-white/[0.04] flex items-center gap-3">
                    <span className="text-[9px] text-slate-600 font-mono bg-white/[0.03] px-2 py-0.5 rounded">🔗 {e.content_hash.substring(0,20)}…</span>
                    {e.prev_hash && e.prev_hash !== "0".repeat(64) && <span className="text-[9px] text-slate-700 font-mono">← {e.prev_hash.substring(0,12)}…</span>}
                    {e.prev_hash === "0".repeat(64) && <span className="text-[9px] text-blue-500/50 font-mono">genesis block</span>}
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
