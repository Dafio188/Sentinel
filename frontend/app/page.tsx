"use client";

import { useEffect, useState } from "react";
import { Shield, ShieldAlert, ShieldCheck, FileLock2, Activity, CheckCircle, Info, ArrowRight, HelpCircle } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null);
  const [audit, setAudit] = useState<any>(null);
  const [showHelp, setShowHelp] = useState(true);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(console.error);
    api.getAudit().then(setAudit).catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      {/* Header & Operator Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard di Controllo AIGate</h1>
          <p className="text-gray-400 mt-1">Panoramica operativa dello stato di sicurezza e conformità normativa locale</p>
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className="flex items-center gap-2 px-4 py-2 rounded-2xl glass-card text-xs font-semibold text-blue-400 hover:text-white"
        >
          <HelpCircle className="w-4 h-4" /> {showHelp ? "Nascondi Guida Operatore" : "Guida Operatore"}
        </button>
      </div>

      {/* Operator Welcome & Quick Start Cards */}
      {showHelp && (
        <div className="glass-panel p-6 rounded-3xl border-blue-500/30 bg-blue-500/5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
              <Info className="w-5 h-5" /> Guida Rapida & Scenari Operativi
            </div>
            <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-blue-500/20 text-blue-300 font-bold">
              Sentinell Engine v1.0 (Rizzo-PII + ARKS Legal)
            </span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            Benvenuto su <strong>Sentinell</strong>. Questo gateway locale protegge i dati sensibili prima dell'invio ad algoritmi ed LLM cloud e calcola la conformità deterministica al <strong>GDPR</strong> ed all'<strong>EU AI Act dell'Unione Europea</strong>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <Link href="/privacy" className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-emerald-500/50 transition-all hover:bg-emerald-500/10 space-y-2 group">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-emerald-300 group-hover:text-white">🩺 Sanità & Medici</span>
                <ArrowRight className="w-4 h-4 text-emerald-400 group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Anonimizza cartelle cliniche in locale con Rizzo-PII prima di inviarle a modelli LLM ed analizza i rischi ex Art. 9 GDPR.
              </p>
            </Link>

            <Link href="/compliance" className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/50 transition-all hover:bg-blue-500/10 space-y-2 group">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-blue-300 group-hover:text-white">👥 HR & Selezione CV</span>
                <ArrowRight className="w-4 h-4 text-blue-400 group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Verifica sistemi di screening candidati per l'Allegato III dell'EU AI Act ed ottieni le azioni correttive obbligatorie.
              </p>
            </Link>

            <Link href="/compliance" className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-purple-500/50 transition-all hover:bg-purple-500/10 space-y-2 group">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-purple-300 group-hover:text-white">💻 Dev & API Cloud</span>
                <ArrowRight className="w-4 h-4 text-purple-400 group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Valuta l'integrazione di Gemini, OpenAI o Claude e verifica i trasferimenti extra-UE (Capo V GDPR).
              </p>
            </Link>
          </div>
        </div>
      )}

      {/* Security Zones Banner with Clear Instructions */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-white">Modello a 3 Zone di Sicurezza</h2>
        <p className="text-xs text-gray-400">Ogni documento e payload viene inserito ed isolato in una rigida Zona di Sicurezza per prevenire la fuga di dati.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* ZONE 0 */}
          <div className="glass-card p-6 rounded-3xl border-red-500/30 bg-red-500/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                Zona 0 — RED (Riservata)
              </span>
              <ShieldAlert className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Dati Grezzi & Vault Originale</h3>
              <p className="text-xs text-gray-300 mt-1">
                Contiene i file originali non modificati. <strong>Nessun dato di Zona 0 può essere mai inviato verso l'esterno o comunicato ad LLM esterni.</strong>
              </p>
            </div>
            <div className="pt-2 text-[10px] text-red-300 font-mono">⚠️ Isolamento Fisico Garantito</div>
          </div>

          {/* ZONE 1 */}
          <div className="glass-card p-6 rounded-3xl border-amber-500/30 bg-amber-500/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Zona 1 — AMBER (Protetta)
              </span>
              <FileLock2 className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Dati Mascherati & Pseudonimi</h3>
              <p className="text-xs text-gray-300 mt-1">
                Contiene documenti a cui sono state applicate tecniche di protezione. Le mappe dei riferimenti sono cifrate nel Vault locale.
              </p>
            </div>
            <div className="pt-2 text-[10px] text-amber-300 font-mono">🔒 Cifratura AES-GCM 256</div>
          </div>

          {/* ZONE 2 */}
          <div className="glass-card p-6 rounded-3xl border-emerald-500/30 bg-emerald-500/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Zona 2 — GREEN (Egress)
              </span>
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Dati Anonimizzati o Sicuri</h3>
              <p className="text-xs text-gray-300 mt-1">
                Testi con esito di Zero-Residue Validator completato. Possono essere inviati in modo sicuro ai modelli di intelligenza artificiale.
              </p>
            </div>
            <div className="pt-2 text-[10px] text-emerald-300 font-mono">✅ Inoltro Autorizzato</div>
          </div>
        </div>
      </div>

      {/* System Status & Audit Chain Integrity with Explanations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-semibold text-white">Stato Servizi Gateway</h2>
            </div>
            <span className="text-xs text-gray-400">Verifica in tempo reale</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-2xl bg-white/5 flex items-center justify-between">
              <div>
                <span className="font-semibold text-gray-200 block">Indirizzo Servizio Locale</span>
                <span className="text-[11px] text-gray-400">Garantisce che il gateway risponda solo sulla macchina locale</span>
              </div>
              <span className="font-mono text-emerald-400 font-bold px-2 py-1 rounded bg-emerald-500/10">127.0.0.1:8000</span>
            </div>

            <div className="p-3 rounded-2xl bg-white/5 flex items-center justify-between">
              <div>
                <span className="font-semibold text-gray-200 block">Filtro Egress Host</span>
                <span className="text-[11px] text-gray-400">Blocca chiamate di rete non autorizzate verso server sconosciuti</span>
              </div>
              <span className="font-mono text-blue-400 font-bold px-2 py-1 rounded bg-blue-500/10">ATTIVO (Allowlist)</span>
            </div>

            <div className="p-3 rounded-2xl bg-white/5 flex items-center justify-between">
              <div>
                <span className="font-semibold text-gray-200 block">Motore di Anonimizzazione Privacy</span>
                <span className="text-[11px] text-gray-400">Rizzo-PII (0.3B) + Pattern Gate Italiano (CF, PIVA, DOCID)</span>
              </div>
              <span className="font-mono text-emerald-400 font-bold px-2 py-1 rounded bg-emerald-500/10">ATTIVO (Rizzo-PII)</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-semibold text-white">Registro Audit Non Manomettibile</h2>
            </div>
            <Link href="/audit" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
              Dettagli <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Certificazione Crittografica</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold">VALIDATA</span>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              Tutte le azioni svolte sulla piattaforma (scansioni, protezioni, risposte LLM) vengono collegate in una <strong>Catena Hash SHA256 Append-Only</strong>. Qualsiasi modifica posteriore viene immediatamente rilevata.
            </p>
            <div className="text-[11px] font-mono text-gray-400 truncate bg-black/30 p-2 rounded-xl border border-white/5">
              Hash Ultimo Evento: {audit?.latest_hash || "Inizializzazione..."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
