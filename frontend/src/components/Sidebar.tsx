"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard", icon: "📊", desc: "Overview" },
  { href: "/alerts", label: "Alerts", icon: "🚨", desc: "Security events" },
  { href: "/investigations", label: "Investigations", icon: "🔍", desc: "AI analysis" },
  { href: "/evaluation", label: "Evaluation", icon: "📈", desc: "Metrics" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="fixed left-0 top-0 h-screen w-[272px] glass border-r border-white/[0.06] flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="relative">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-500 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-blue-500/25">
              Ai
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-[#0a0e1a] animate-glow-pulse" />
          </div>
          <div>
            <h1 className="text-[17px] font-extrabold text-white tracking-tight">AiSOC</h1>
            <p className="text-[10px] text-blue-400/60 uppercase tracking-[0.2em] font-semibold">Security Operations</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-0.5">
        <p className="px-4 py-2 text-[10px] text-slate-500 uppercase tracking-[0.15em] font-semibold">Menu</p>
        {NAV.map((item) => {
          const active = item.href === "/" ? path === "/" : path.startsWith(item.href);
          return (
            <Link key={item.href} href={item.href}
              className={`group flex items-center gap-3.5 px-4 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-300 relative overflow-hidden ${
                active
                  ? "bg-gradient-to-r from-blue-500/15 to-cyan-500/10 text-blue-300 shadow-lg shadow-blue-500/5"
                  : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
              }`}>
              {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />}
              <span className="text-[17px] transition-transform duration-300 group-hover:scale-110">{item.icon}</span>
              <div>
                <span className="block">{item.label}</span>
                <span className={`block text-[10px] -mt-0.5 ${active ? "text-blue-400/50" : "text-slate-600"}`}>{item.desc}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Features */}
      <div className="p-3 space-y-2">
        <div className="px-4 py-3 rounded-xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/[0.04]">
          <p className="text-[9px] text-slate-500 uppercase tracking-[0.2em] font-semibold mb-2">Active Modules</p>
          <div className="flex flex-wrap gap-1">
            {["OCSF", "SHA-256", "Pseudonymize", "Correlation", "Gemini AI"].map((f) => (
              <span key={f} className="px-1.5 py-0.5 bg-blue-500/8 text-blue-400/70 border border-blue-500/10 rounded-md text-[9px] font-medium">{f}</span>
            ))}
          </div>
        </div>
        <div className="px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500/[0.08] via-purple-500/[0.05] to-cyan-500/[0.08] border border-blue-500/10">
          <p className="text-[10px] text-blue-400/80 font-bold tracking-wide">CAPSTONE PROJECT</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Group 4 · PCCOE Pune</p>
          <p className="text-[9px] text-slate-600 mt-0.5">CSE (AI & ML) · 2026-27</p>
        </div>
      </div>
    </aside>
  );
}
