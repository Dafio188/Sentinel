"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Lock, FileText, Cpu, CheckCircle2, Info } from "lucide-react";

const navItems = [
  {
    label: "Dashboard",
    href: "/",
    icon: Shield,
    tooltip: "Panoramica delle 3 Zone di Sicurezza e stato della Catena di Audit",
  },
  {
    label: "Privacy Center",
    href: "/privacy",
    icon: Lock,
    tooltip: "Caricamento file, scansione PII ed anonimizzazione (Zona 0 ➔ Zona 1)",
  },
  {
    label: "Compliance Wizard",
    href: "/compliance",
    icon: FileText,
    tooltip: "Valutazione di conformità legale (GDPR + EU AI Act) e report cromatici",
  },
  {
    label: "LLM Gateway",
    href: "/gateway",
    icon: Cpu,
    tooltip: "Chat protetta con Ollama locale ed LLM esterni previa scansione Privacy Gate",
  },
  {
    label: "Audit & ARKS",
    href: "/audit",
    icon: CheckCircle2,
    tooltip: "Registro eventi non manomettibile ed approvazione versioni Knowledge Base",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 glass-panel border-r border-white/10 flex flex-col justify-between p-6 z-50">
      <div>
        <div className="flex items-center gap-3 mb-10">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-lg text-white tracking-tight">AIGate</h1>
            <p className="text-xs text-gray-400">Local Privacy & AI Gateway</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                title={item.tooltip}
                className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-md shadow-blue-500/10"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? "text-blue-400" : "text-gray-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="glass-card p-4 rounded-2xl space-y-2">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Stato Gateway</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
        <p className="text-xs font-semibold text-white">127.0.0.1 (Sicuro)</p>
        <p className="text-[10px] text-gray-400 leading-tight">Interfaccia protetta per operatore locale</p>
      </div>
    </aside>
  );
}
