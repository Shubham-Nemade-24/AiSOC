"use client";
import { useEffect, useState } from "react";
import { fetchDashboard } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const SEV_COLORS: Record<string, string> = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#3b82f6", info: "#6b7280" };

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const load = () => {
    fetchDashboard().then((d) => { setData(d); setLastUpdate(new Date()); }).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="flex items-center justify-center h-96"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!data) return <p className="text-red-400">Failed to load. Is the backend running on port 8000?</p>;

  const sevData = Object.entries(data.by_severity || {}).map(([name, value]) => ({ name, value }));
  const srcData = Object.entries(data.by_source || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">SOC Dashboard</h1>
          <p className="text-gray-500 mt-1">Real-time security operations overview</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-green-400 font-medium">LIVE</span>
          <span className="text-xs text-gray-500">updated {lastUpdate.toLocaleTimeString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Alerts" value={data.total_alerts} icon="🚨" color="blue" />
        <StatCard label="Critical" value={data.by_severity?.critical || 0} icon="🔴" color="red" />
        <StatCard label="AI Triaged" value={`${data.ai_triage?.triage_rate || 0}%`} icon="🤖" color="green" />
        <StatCard label="Investigations" value={data.investigations?.completed || 0} icon="🔍" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-soc-card border border-soc-border rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Alerts by Severity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={sevData}>
              <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} />
              <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} />
              <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: "8px", color: "#e5e7eb" }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {sevData.map((entry: any, i: number) => <Cell key={i} fill={SEV_COLORS[entry.name] || "#6b7280"} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-soc-card border border-soc-border rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Alerts by Source</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={srcData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, value }: any) => `${name}: ${value}`}>
                {srcData.map((_: any, i: number) => <Cell key={i} fill={["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"][i % 6]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: "8px", color: "#e5e7eb" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-soc-card border border-soc-border rounded-xl p-6">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Pipeline Status</h3>
        <div className="grid grid-cols-5 gap-4">
          {Object.entries(data.by_status || {}).map(([status, count]: any) => (
            <div key={status} className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
              <p className="text-2xl font-bold text-white">{count}</p>
              <p className="text-xs text-gray-500 uppercase mt-1">{status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: { label: string; value: any; icon: string; color: string }) {
  const bg = { blue: "from-blue-500/10 to-blue-600/5", red: "from-red-500/10 to-red-600/5", green: "from-green-500/10 to-green-600/5", purple: "from-purple-500/10 to-purple-600/5" }[color] || "";
  const border = { blue: "border-blue-500/20", red: "border-red-500/20", green: "border-green-500/20", purple: "border-purple-500/20" }[color] || "";
  return (
    <div className={`bg-gradient-to-br ${bg} border ${border} rounded-xl p-5 transition-all hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
        </div>
        <span className="text-3xl opacity-60">{icon}</span>
      </div>
    </div>
  );
}
