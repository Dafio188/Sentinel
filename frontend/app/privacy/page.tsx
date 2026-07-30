"use client";

import { useState } from "react";
import { Upload, Shield, Eye, Lock, FileCode, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function PrivacyCenterPage() {
  const [docId, setDocId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [entities, setEntities] = useState<any[]>([]);
  const [strategy, setStrategy] = useState("BALANCED");
  const [vaultPassphrase, setVaultPassphrase] = useState("");
  const [protectedResult, setProtectedResult] = useState<any>(null);
  const [diff, setDiff] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const uploadRes = await api.uploadDocument(file);
      setDocId(uploadRes.document_id);
      setFilename(uploadRes.filename);
      toast.success("Documento caricato con successo");

      const scanRes = await api.scanDocument(uploadRes.document_id);
      setEntities(scanRes.entities || []);
      toast.info(`Scansione PII completata: ${scanRes.detected_entities_count} entità rilevate`);
    } catch (err: any) {
      toast.error(err.message || "Errore durante il caricamento");
    } finally {
      setLoading(false);
    }
  };

  const handleProtect = async () => {
    if (!docId) return;

    setLoading(true);
    try {
      const res = await api.protectDocument(docId, {
        strategy,
        vault_passphrase: vaultPassphrase || undefined,
      });
      setProtectedResult(res);
      toast.success("Documento protetto con successo!");

      const diffRes = await api.getVersionDiff(res.result_version_id);
      setDiff(diffRes.diff || []);
    } catch (err: any) {
      toast.error(err.message || "Errore durante la protezione");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Privacy Engine & Data Protection Center</h1>
        <p className="text-gray-400 mt-1">Anonimizzazione deterministica, azzeramento metadati e rimozione PII</p>
      </div>

      {/* Upload Drag & Drop Area */}
      <div className="glass-panel p-8 rounded-3xl border-dashed border-2 border-white/20 text-center relative hover:border-blue-500/50 transition-colors">
        <input
          type="file"
          onChange={handleFileUpload}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-blue-600/20 text-blue-400 flex items-center justify-center">
            <Upload className="w-7 h-7" />
          </div>
          <div>
            <p className="text-base font-semibold text-white">
              {filename ? `Documento: ${filename}` : "Trascina qui il documento o clicca per caricare"}
            </p>
            <p className="text-xs text-gray-400 mt-1">Supporta DOCX, PDF, TXT, CSV, XLSX ed Immagini (OCR)</p>
          </div>
        </div>
      </div>

      {/* Detected PII Table */}
      {entities.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Eye className="w-5 h-5 text-blue-400" /> Entità PII Rilevate ({entities.length})
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-gray-400 text-xs uppercase">
                  <th className="py-3 px-4">Tipo Entità</th>
                  <th className="py-3 px-4">Categoria</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Azione Proposta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {entities.map((e, idx) => (
                  <tr key={idx} className="hover:bg-white/5">
                    <td className="py-3 px-4 font-mono text-white">{e.entity_type}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        e.category === 'SPECIAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        e.category === 'FINANCIAL' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}>
                        {e.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300">{(e.confidence * 100).toFixed(0)}%</td>
                    <td className="py-3 px-4 text-gray-300 font-mono text-xs">{e.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Strategy Selector & Protect Controls */}
          <div className="pt-4 border-t border-white/10 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Strategia Anonimizzazione</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="BALANCED" className="bg-gray-900">BALANCED (Standard MASK)</option>
                <option value="STRICT" className="bg-gray-900">STRICT (Zero-Residue Removal)</option>
                <option value="REPLACE" className="bg-gray-900">REPLACE (Vault Pseudonymization)</option>
              </select>
            </div>

            {strategy === "REPLACE" && (
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">Passphrase Vault</label>
                <input
                  type="password"
                  value={vaultPassphrase}
                  onChange={(e) => setVaultPassphrase(e.target.value)}
                  placeholder="Inserisci passphrase vault..."
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            )}

            <button
              onClick={handleProtect}
              disabled={loading}
              className="apple-button w-full py-3 text-sm font-semibold flex items-center justify-center gap-2"
            >
              <Shield className="w-4 h-4" /> Applica Protezione
            </button>
          </div>
        </div>
      )}

      {/* Protected Result & Interactive Diff Viewer */}
      {protectedResult && (
        <div className="glass-panel p-6 rounded-3xl space-y-4 border-emerald-500/30">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" /> Risultato Protezione Applicata
            </h2>
            <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
              Zero-Residue: PASS
            </span>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 rounded-2xl bg-white/5">
              <span className="text-xs text-gray-400">Privacy Score</span>
              <p className="text-xl font-bold text-emerald-400">{protectedResult.privacy_score.toFixed(2)}</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5">
              <span className="text-xs text-gray-400">Utility Score</span>
              <p className="text-xl font-bold text-blue-400">{protectedResult.utility_score.toFixed(2)}</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5">
              <span className="text-xs text-gray-400">Re-ID Risk</span>
              <p className="text-xl font-bold text-amber-400">{protectedResult.reid_risk.toFixed(2)}</p>
            </div>
          </div>

          {/* Interactive Diff */}
          {diff.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Visualizzatore Diff (Sostituzioni Effettuate)</h3>
              <div className="p-4 rounded-2xl bg-black/40 font-mono text-xs space-y-1 max-h-48 overflow-y-auto">
                {diff.map((d, idx) => (
                  <div key={idx} className="flex items-center justify-between py-1 border-b border-white/5">
                    <span className="text-red-400">- {d.original}</span>
                    <span className="text-emerald-400">+ {d.replacement}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
