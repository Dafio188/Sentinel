"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Database, CheckCircle2, AlertOctagon, HelpCircle, Info, Lock } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function AuditPage() {
  const [audit, setAudit] = useState<any>(null);
  const [kbVersions, setKbVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(true);

  const fetchAuditData = () => {
    api.getAudit().then(setAudit).catch(console.error);
    api.getKbVersions().then((res) => setKbVersions(res.versions || [])).catch(console.error);
  };

  useEffect(() => {
    fetchAuditData();
  }, []);

  const handleApproveKb = async (id: string) => {
    setLoading(true);
    try {
      await api.approveKbVersion(id);
      toast.success(`Versione KB ${id} approvata con successo!`);
      fetchAuditData();
    } catch (err: any) {
      toast.error("Errore durante l'approvazione della versione KB");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Registro Audit & Knowledge Base ARKS</h1>
          <p className="text-gray-400 mt-1">Integrità crittografica SHA256 dei log ed approvazione umana delle basi normative</p>
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className="flex items-center gap-2 px-4 py-2 rounded-2xl glass-card text-xs font-semibold text-blue-400 hover:text-white"
        >
          <HelpCircle className="w-4 h-4" /> {showHelp ? "Nascondi Istruzioni Operatore" : "Istruzioni Operatore"}
        </button>
      </div>

      {/* Operator Instructions Banner */}
      {showHelp && (
        <div className="glass-panel p-6 rounded-3xl border-emerald-500/30 bg-emerald-500/5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-300 font-semibold text-sm">
            <Info className="w-5 h-5" /> Guida Operativa all'Audit & Versionamento Normativo
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-300">
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">Integrità Registro Audit</span>
              <p className="text-gray-400">Ogni evento viene concatenato con l'hash SHA256 della riga precedente (Invariante I3). Se un log viene alterato o eliminato, la verifica evidenzia la manomissione.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">Approvazione Umana KB Normativa</span>
              <p className="text-gray-400">Le versioni delle regole di conformità (es. AI Act post-Omnibus) richiedono la firma/approvazione esplicita dell'operatore umano prima dell'entrata in vigore.</p>
            </div>
          </div>
        </div>
      )}

      {/* Audit Chain Verification Box */}
      <div className="glass-panel p-8 rounded-3xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Verifica Integrità Catena Hash Audit</h2>
            <p className="text-xs text-gray-400 mt-1">Convalida matematica dei log di sistema (Invariante I3 Append-Only)</p>
          </div>
          <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${
            audit?.chain_valid ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" : "bg-red-500/20 text-red-300 border-red-500/30"
          }`}>
            {audit?.chain_valid ? "Integrità Valida ✅" : "Manomissione Rilevata ⚠️"}
          </span>
        </div>

        <div className="p-6 rounded-2xl bg-black/40 border border-white/10 space-y-3">
          <div className="flex justify-between items-center text-xs">
            <span className="text-gray-400">Stato Catena Audit:</span>
            <span className="font-bold text-emerald-400">{audit?.chain_valid ? "Nessuna alterazione rilevata" : `Alterazione alla sequenza #${audit?.first_tampered_seq}`}</span>
          </div>

          <div className="flex justify-between items-center text-xs">
            <span className="text-gray-400">Hash Ultimo Registro (SHA256):</span>
            <span className="font-mono text-blue-400 font-bold text-[11px] truncate max-w-xs">{audit?.latest_hash || "..."}</span>
          </div>
        </div>
      </div>

      {/* KB Versions Approval Manager */}
      <div className="glass-panel p-6 rounded-3xl space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-white">Versionamento Basi Normative ARKS</h2>
          <p className="text-xs text-gray-400 mt-1">Approvazione formale dell'operatore per l'entrata in vigore dei corpus giuridici</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {kbVersions.map((v) => (
            <div key={v.id} className="p-5 rounded-3xl glass-card space-y-3 border-white/10">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white">{v.id}</span>
                <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full ${
                  v.active ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-gray-500/20 text-gray-400"
                }`}>
                  {v.active ? "ATTIVA" : "DRAFT"}
                </span>
              </div>

              <p className="text-xs text-gray-300">{v.notes}</p>

              <div className="flex items-center justify-between pt-2">
                <span className="text-[11px] text-gray-400">
                  {v.approved_by_human ? "Approvata da Operatore Umano ✅" : "Richiede Firma Operatore ⚠️"}
                </span>

                {!v.approved_by_human && (
                  <button
                    onClick={() => handleApproveKb(v.id)}
                    disabled={loading}
                    className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-blue-500/20"
                    title="Approva formalmente l'adozione di questa versione della Knowledge Base"
                  >
                    Approva Ora
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
