"use client";
import { useEffect, useState } from "react";

export default function EvaluationPage() {
  const [data, setData] = useState<any>(null);
  const [corr, setCorr] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/dashboard/evaluation").then((r) => r.json()),
      fetch("/api/dashboard/correlations").then((r) => r.json()),
    ]).then(([evalData, corrData]) => { setData(evalData); setCorr(corrData); })
      .catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-96"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!data) return <p className="text-red-400">Failed to load evaluation data.</p>;

  const t = data.triage_metrics;
  const inv = data.investigation_metrics;
  const ledger = data.ledger_integrity;

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-3xl font-bold text-white">Evaluation Harness</h1>
        <p className="text-gray-500 mt-1">System performance metrics & audit integrity</p>
      </div>

      {/* Triage Metrics */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-4">🤖 AI Triage Performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard label="Triage Rate" value={`${t.triage_rate_pct}%`} sub={`${t.triaged}/${t.total_alerts} alerts`} />
          <MetricCard label="Alert Reduction" value={`${t.alert_reduction_rate_pct}%`} sub="FP + benign filtered" />
          <MetricCard label="Avg Confidence" value={`${(t.avg_confidence * 100).toFixed(0)}%`} sub="across all verdicts" />
          <MetricCard label="True Positives" value={t.verdicts.true_positive} sub="confirmed threats" />
        </div>
        <div className="grid grid-cols-4 gap-3">
          {Object.entries(t.verdicts).map(([verdict, count]: any) => {
            const colors: Record<string, string> = { true_positive: "text-red-400 bg-red-500/10", false_positive: "text-green-400 bg-green-500/10", suspicious: "text-yellow-400 bg-yellow-500/10", benign: "text-gray-400 bg-gray-500/10" };
            return (
              <div key={verdict} className={`rounded-lg p-3 text-center ${colors[verdict] || "bg-white/5"}`}>
                <p className="text-2xl font-bold">{count}</p>
                <p className="text-xs mt-1 opacity-70">{verdict.replace("_", " ")}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Investigation Metrics */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <h3 className="text-sm font-semibold text-purple-400 uppercase tracking-wider mb-4">🔍 Investigation Pipeline</h3>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard label="Total Investigations" value={inv.total_investigations} sub="multi-agent pipelines" />
          <MetricCard label="Completion Rate" value={`${inv.completion_rate_pct}%`} sub={`${inv.completed} completed`} />
          <MetricCard label="Avg Risk Score" value={`${inv.avg_risk_score}/10`} sub="across investigations" />
        </div>
      </div>

      {/* Ledger Integrity */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <h3 className="text-sm font-semibold text-green-400 uppercase tracking-wider mb-4">🔒 Ledger Integrity (SHA-256)</h3>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard label="Ledger Entries" value={ledger.total_entries} sub="audit records" />
          <MetricCard label="Hash Coverage" value={`${ledger.hash_coverage_pct}%`} sub={`${ledger.hashed_entries} hashed`} />
          <MetricCard label="Pseudonymized" value={ledger.pseudonymized_entries} sub="privacy-protected calls" />
        </div>
        {ledger.hash_coverage_pct === 100 && ledger.total_entries > 0 && (
          <div className="mt-4 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg">
            <p className="text-sm text-green-400">✓ All ledger entries have valid SHA-256 integrity hashes. Chain is intact.</p>
          </div>
        )}
      </div>

      {/* Alert Correlations */}
      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <h3 className="text-sm font-semibold text-cyan-400 uppercase tracking-wider mb-4">🔗 Alert Correlations</h3>
        {corr?.total_groups > 0 ? (
          <div className="space-y-3">
            {corr.correlations.map((group: any, i: number) => (
              <div key={i} className="border border-soc-border rounded-lg p-4 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">Group {i + 1} — {group.alert_count} correlated alerts</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${group.max_severity === "critical" ? "bg-red-500/10 text-red-400" : group.max_severity === "high" ? "bg-orange-500/10 text-orange-400" : "bg-yellow-500/10 text-yellow-400"}`}>
                    {group.max_severity}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {group.shared_entities.slice(0, 6).map((e: string, j: number) => (
                    <span key={j} className="px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded text-xs font-mono">{e}</span>
                  ))}
                </div>
                <div className="text-xs text-gray-500">
                  Tactics: {group.mitre_tactics.join(", ")} · Span: {group.time_span_minutes}min
                </div>
                <div className="mt-2 text-xs text-gray-400">
                  {group.alert_titles.slice(0, 3).map((t: string, j: number) => (
                    <p key={j}>• {t}</p>
                  ))}
                  {group.alert_titles.length > 3 && <p>...and {group.alert_titles.length - 3} more</p>}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No correlated groups found yet. Correlations form when alerts share IPs, hostnames, or users within a 60-minute window.</p>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value, sub }: { label: string; value: any; sub: string }) {
  return (
    <div className="p-4 rounded-lg bg-white/5 border border-white/10">
      <p className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{sub}</p>
    </div>
  );
}
