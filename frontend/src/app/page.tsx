"use client";
import { useEffect, useState } from "react";
import { fetchDashboard } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Area, AreaChart } from "recharts";

const SEV_COLORS: Record<string, string> = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#3b82f6", info: "#64748b" };
const SEV_GLOW: Record<string, string> = { critical: "shadow-red-500/20", high: "shadow-orange-500/20", medium: "shadow-yellow-500/20", low: "shadow-blue-500/20" };

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const load = () => fetchDashboard().then((d) => { setData(d); setLastUpdate(new Date()); }).catch(console.error).finally(() => setLoading(false));
  useEffect(() => { load(); const i = setInterval(load, 8000); return () => clearInterval(i); }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-[80vh]">
      <div className="relative"><div className="w-12 h-12 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" /><div className="absolute inset-2 rounded-full border-2 border-cyan-500/20 border-b-cyan-500 animate-spin" style={{animationDirection:"reverse",animationDuration:"1.5s"}} /></div>
    </div>
  );
  if (!data) return <div className="glass rounded-2xl p-8 text-center"><p className="text-red-400 text-lg">⚠️ Backend offline</p><p className="text-slate-500 text-sm mt-2">Start the backend on port 8000</p></div>;

  const sevData = Object.entries(data.by_severity || {}).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value, fill: SEV_COLORS[name] }));
  const srcData = Object.entries(data.by_source || {}).map(([name, value]) => ({ name, value }));
  const SRC_COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div className="animate-slide-up">
          <p className="text-blue-400/60 text-xs font-semibold uppercase tracking-[0.2em] mb-1">Security Operations Center</p>
          <h1 className="text-4xl font-extrabold text-white tracking-tight">Dashboard</h1>
        </div>
        <div className="flex items-center gap-2.5 px-4 py-2 glass rounded-full animate-fade-in">
          <div className="relative"><span className="w-2 h-2 rounded-full bg-emerald-400 block" /><span className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-75" /></div>
          <span className="text-[11px] text-emerald-400 font-semibold tracking-wide">LIVE</span>
          <span className="text-[11px] text-slate-500">{lastUpdate.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Alerts", value: data.total_alerts, icon: "🛡️", gradient: "from-blue-500/10 via-blue-600/5 to-transparent", border: "border-blue-500/15", accent: "text-blue-400" },
          { label: "Critical Threats", value: data.by_severity?.critical || 0, icon: "🔴", gradient: "from-red-500/10 via-red-600/5 to-transparent", border: "border-red-500/15", accent: "text-red-400" },
          { label: "AI Triage Rate", value: `${data.ai_triage?.triage_rate || 0}%`, icon: "🤖", gradient: "from-emerald-500/10 via-emerald-600/5 to-transparent", border: "border-emerald-500/15", accent: "text-emerald-400" },
          { label: "Investigations", value: data.investigations?.completed || 0, icon: "🔬", gradient: "from-purple-500/10 via-purple-600/5 to-transparent", border: "border-purple-500/15", accent: "text-purple-400" },
        ].map((card, i) => (
          <div key={i} className={`relative overflow-hidden glass glass-hover rounded-2xl p-5 bg-gradient-to-br ${card.gradient} ${card.border} animate-slide-up`} style={{animationDelay: `${i*80}ms`}}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-[0.15em] font-semibold">{card.label}</p>
                <p className={`text-3xl font-extrabold text-white mt-2 tracking-tight`}>{card.value}</p>
              </div>
              <span className="text-2xl opacity-50 animate-float" style={{animationDelay:`${i*0.5}s`}}>{card.icon}</span>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-5">
        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"200ms"}}>
          <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.15em] mb-5">Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={sevData} barSize={36}>
              <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: "rgba(255,255,255,0.02)" }} contentStyle={{ background: "rgba(15,23,42,0.95)", border: "1px solid rgba(56,78,126,0.3)", borderRadius: 12, color: "#e2e8f0", boxShadow: "0 20px 40px rgba(0,0,0,0.3)", backdropFilter: "blur(20px)", fontSize: 12 }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {sevData.map((entry: any, i: number) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"280ms"}}>
          <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.15em] mb-5">Alert Sources</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={srcData} cx="50%" cy="50%" innerRadius={55} outerRadius={95} paddingAngle={4} dataKey="value" strokeWidth={0}
                label={({ name, value }: any) => `${name} (${value})`} labelLine={{ stroke: "#475569", strokeWidth: 1 }}>
                {srcData.map((_: any, i: number) => <Cell key={i} fill={SRC_COLORS[i % SRC_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "rgba(15,23,42,0.95)", border: "1px solid rgba(56,78,126,0.3)", borderRadius: 12, color: "#e2e8f0", boxShadow: "0 20px 40px rgba(0,0,0,0.3)", fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pipeline + AI Verdict */}
      <div className="grid grid-cols-5 gap-3 animate-slide-up" style={{animationDelay:"360ms"}}>
        {Object.entries(data.by_status || {}).map(([status, count]: any, i: number) => (
          <div key={status} className="glass glass-hover rounded-xl p-4 text-center group">
            <p className="text-2xl font-extrabold text-white group-hover:text-gradient transition-colors">{count}</p>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-1 font-semibold">{status}</p>
            {i < 4 && <div className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-700 text-xs hidden lg:block">→</div>}
          </div>
        ))}
      </div>

      {/* AI Verdicts Row */}
      <div className="glass rounded-2xl p-6 animate-slide-up" style={{animationDelay:"440ms"}}>
        <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.15em] mb-4">AI Triage Verdicts</h3>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "True Positive", value: data.ai_triage?.true_positives || 0, color: "red" },
            { label: "False Positive", value: data.ai_triage?.false_positives || 0, color: "green" },
            { label: "Suspicious", value: data.ai_triage?.suspicious || 0, color: "yellow" },
            { label: "Benign", value: data.ai_triage?.benign || 0, color: "slate" },
          ].map((v) => {
            const bg = { red: "from-red-500/10", green: "from-emerald-500/10", yellow: "from-yellow-500/10", slate: "from-slate-500/10" }[v.color];
            const text = { red: "text-red-400", green: "text-emerald-400", yellow: "text-yellow-400", slate: "text-slate-400" }[v.color];
            return (
              <div key={v.label} className={`rounded-xl p-4 bg-gradient-to-br ${bg} to-transparent border border-white/[0.04]`}>
                <p className={`text-3xl font-extrabold ${text}`}>{v.value}</p>
                <p className="text-[10px] text-slate-500 uppercase mt-1 font-semibold tracking-wider">{v.label}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
