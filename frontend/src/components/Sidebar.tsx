"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/alerts", label: "Alerts", icon: "🚨" },
  { href: "/investigations", label: "Investigations", icon: "🔍" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-soc-card border-r border-soc-border flex flex-col z-50">
      <div className="p-6 border-b border-soc-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white font-bold text-lg">
            Ai
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">AiSOC</h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Security Operations</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {NAV.map((item) => {
          const active = item.href === "/" ? path === "/" : path.startsWith(item.href);
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                active
                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20 glow-blue"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}>
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-soc-border">
        <div className="px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
          <p className="text-[10px] text-blue-400 uppercase tracking-wider font-semibold">Capstone Project</p>
          <p className="text-xs text-gray-400 mt-1">Group 4 · PCCOE Pune</p>
          <p className="text-[10px] text-gray-500 mt-0.5">AI & ML · 2026-2027</p>
        </div>
      </div>
    </aside>
  );
}
