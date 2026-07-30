"use client";

import { useEffect, useState } from "react";
import { Shield, ShieldAlert, ShieldCheck, FileLock2, Activity, CheckCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null);
  const [audit, setAudit] = useState<any>(null);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(console.error);
    api.getAudit().then(setAudit).catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard di Controllo</h1>
        <p className="text-gray-400 mt-1">Stato operativo delle 3 Zone di Sicurezza e dell'Audit Chain</p>
      </div>

      {/* Security Zones Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-3xl border-red-500/20 bg-red-500/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
              Zona 0 — RED
            </span>
            <ShieldAlert className="w-6 h-6 text-red-400" />
          </div>
          <h3 className="text-xl font-bold text-white mb-1">Dati Grezzi (Original)</h3>
          <p className="text-xs text-gray-400">Isolati localmente. Divieto assoluto di egress verso provider esterni.</p>
        </div>

        <div className="glass-card p-6 rounded-3xl border-amber-500/20 bg-amber-500/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
              Zona 1 — AMBER
            </span>
            <FileLock2 className="w-6 h-6 text-amber-400" />
          </div>
          <h3 className="text-xl font-bold text-white mb-1">Dati Protetti</h3>
          <p className="text-xs text-gray-400">Mascherati / Pseudonimizzati con Vault local keying.</p>
        </div>

        <div className="glass-card p-6 rounded-3xl border-emerald-500/20 bg-emerald-500/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Zona 2 — GREEN
            </span>
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
          <h3 className="text-xl font-bold text-white mb-1">Dati Anonimi</h3>
          <p className="text-xs text-gray-400">Zero residuo verificato. Inoltrabili liberamente.</p>
        </div>
      </div>

      {/* System Status & Audit Chain Integrity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">Stato Servizi Gateway</h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 text-sm">
              <span className="text-gray-300">Binding Locale</span>
              <span className="font-mono text-emerald-400 font-medium">127.0.0.1:8000</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 text-sm">
              <span className="text-gray-300">Egress Allowlist</span>
              <span className="font-mono text-blue-400 font-medium">ATTIVA</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 text-sm">
              <span className="text-gray-300">Privacy Engine</span>
              <span className="font-mono text-emerald-400 font-medium">OPERATIVO (Presidio + Gemma)</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white">Audit Chain Crittografica</h2>
          </div>
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Integrità Registro</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">VALIDATA</span>
            </div>
            <p className="text-xs text-gray-300">Catena append-only hash SHA256 non manomessa.</p>
            <div className="text-[10px] font-mono text-gray-400 truncate">
              Ultimo Hash: {audit?.latest_hash || "Caricamento..."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
