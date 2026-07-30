"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, ShieldCheck, Database, RefreshCw, AlertOctagon } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function AuditPage() {
  const [auditVerify, setAuditVerify] = useState<any>(null);
  const [kbVersions, setKbVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    api.getAudit().then(setAuditVerify).catch(console.error);
    api.getKbVersions().then((res) => setKbVersions(res.versions || [])).catch(console.error);
  };

  const handleVerifyAudit = async () => {
    setLoading(true);
    try {
      const res = await api.getAudit();
      setAuditVerify(res);
      if (res.chain_valid) {
        toast.success("Catena di Audit Verificata: Nessuna manomissione rilevata!");
      } else {
        toast.error(`Allarme Integrità Audit! Rilevata manomissione alla sequenza ${res.first_tampered_seq}`);
      }
    } catch (err: any) {
      toast.error("Errore durante la verifica dell'audit chain");
    } finally {
      setLoading(false);
    }
  };

  const handleApproveKb = async (id: string) => {
    try {
      await api.approveKbVersion(id);
      toast.success(`Versione KB ${id} confermata ed approvata dall'utente!`);
      loadData();
    } catch (err: any) {
      toast.error("Errore approvazione KB");
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Audit Chain & Regulatory Knowledge Center (ARKS)</h1>
        <p className="text-gray-400 mt-1">Verifica di integrità del registro crittografico e gestione delle versioni normative</p>
      </div>

      {/* Audit Chain Cryptographic Verifier */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" /> Registro Audit Append-Only SHA256
          </h2>
          <button
            onClick={handleVerifyAudit}
            disabled={loading}
            className="apple-button px-5 py-2.5 text-xs font-semibold flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Verifica Integrità Catena
          </button>
        </div>

        {auditVerify && (
          <div className={`p-4 rounded-2xl border ${
            auditVerify.chain_valid
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-red-500/10 border-red-500/30 text-red-300"
          }`}>
            <div className="flex items-center justify-between font-semibold text-sm">
              <span>{auditVerify.chain_valid ? "🟢 Catena Intatta ed Incorrotta" : "🔴 Allarme Manomissione Rilevato!"}</span>
              <span className="font-mono text-xs">Ultimo Hash: {auditVerify.latest_hash?.slice(0, 16)}...</span>
            </div>
          </div>
        )}
      </div>

      {/* ARKS Knowledge Base Versions */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-400" /> Versioni della Knowledge Base Normativa (ARKS)
        </h2>

        <div className="space-y-3">
          {kbVersions.map((kb) => (
            <div
              key={kb.id}
              className="glass-card p-4 rounded-2xl flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white text-sm">{kb.id}</span>
                  {kb.active && (
                    <span className="px-2 py-0.5 rounded text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold">
                      ATTIVA (Default)
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-0.5">{kb.notes}</p>
              </div>

              <div>
                {kb.approved_by_human === 1 ? (
                  <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium">
                    <CheckCircle2 className="w-4 h-4" /> Approvata da Utente
                  </span>
                ) : (
                  <button
                    onClick={() => handleApproveKb(kb.id)}
                    className="apple-button px-4 py-2 text-xs font-semibold"
                  >
                    Conferma e Attiva
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
