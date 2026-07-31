"use client";

import { useState } from "react";
import { Upload, ShieldCheck, Lock, Unlock, Eye, FileText, CheckCircle2, AlertTriangle, Info, HelpCircle, Download } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function PrivacyPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docData, setDocData] = useState<any>(null);
  const [entities, setEntities] = useState<any[]>([]);
  const [strategy, setStrategy] = useState<string>("MASK");
  const [vaultPass, setVaultPass] = useState<string>("");
  const [protectResult, setProtectResult] = useState<any>(null);
  const [diff, setDiff] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [showHelp, setShowHelp] = useState<boolean>(true);

  const handleUpload = async () => {
    if (!file) return toast.error("Seleziona un file da caricare");
    setLoading(true);
    try {
      const res = await api.uploadDocument(file);
      setDocData(res);
      toast.success("Documento caricato ed estratto con successo");
      
      // Auto scan
      const scanRes = await api.scanDocument(res.document_id);
      setEntities(scanRes.entities);
      toast.info(`Scansione completata: rilevate ${scanRes.entities.length} entità sensibili`);
    } catch (err: any) {
      toast.error(err.message || "Errore durante il caricamento");
    } finally {
      setLoading(false);
    }
  };

  const handleProtect = async () => {
    if (!docData) return toast.error("Carica prima un documento");
    setLoading(true);
    try {
      const res = await api.protectDocument(docData.document_id, {
        strategy,
        vault_passphrase: vaultPass || undefined,
      });
      setProtectResult(res);
      toast.success("Protezione del documento completata con successo!");

      // Fetch diff
      const diffRes = await api.getVersionDiff(res.result_version_id);
      setDiff(diffRes.diff);
    } catch (err: any) {
      toast.error(err.message || "Errore durante l'anonimizzazione");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!protectResult) return;
    try {
      const filename = protectResult.export_filename || "documento_protetto.txt";
      await api.downloadVersionFile(protectResult.result_version_id, filename);
      toast.success(`Download di ${filename} avviato con successo!`);
    } catch (err: any) {
      toast.error(err.message || "Errore durante il download del file");
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Privacy Center & Anonimizzazione</h1>
          <p className="text-gray-400 mt-1">Isolamento, rilevamento PII e sanitizzazione dei documenti aziendali (Zona 0 ➔ Zona 1)</p>
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
        <div className="glass-panel p-6 rounded-3xl border-purple-500/30 bg-purple-500/5 space-y-3">
          <div className="flex items-center gap-2 text-purple-300 font-semibold text-sm">
            <Info className="w-5 h-5" /> Guida Operativa per la Bonifica Documenti
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-gray-300">
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-purple-300">Passo 1: Caricamento</span>
              <p className="text-gray-400">Trascina o seleziona un file (DOCX, PDF, CSV, TXT o immagini scannerizzate). Il file originale resta custodito in Zona 0.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-purple-300">Passo 2: Scansione PII</span>
              <p className="text-gray-400">Il motore analizza il testo per identificare Codici Fiscali, Partite IVA, IBAN, Nomi e dati personali.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-purple-300">Passo 3: Scelta Strategia</span>
              <p className="text-gray-400">Scegli tra Oscuramento (MASK), Pseudonimizzazione Cifrata (REPLACE con Vault), Generalizzazione o Eliminazione.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-purple-300">Passo 4: Validazione</span>
              <p className="text-gray-400">Verifica la tabella delle differenze e l'esito dello Zero-Residue Validator prima dell'invio agli LLM.</p>
            </div>
          </div>
        </div>
      )}

      {/* Upload Box */}
      <div className="glass-panel p-8 rounded-3xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">1. Caricamento ed Estrazione Documento</h2>
            <p className="text-xs text-gray-400 mt-1">Formati supportati: DOCX, PDF, CSV, TXT, PNG, JPG (OCR integrato)</p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
            Origine ➔ Zona 0 (Strict Local)
          </span>
        </div>

        <div className="border-2 border-dashed border-white/10 rounded-2xl p-8 text-center hover:border-blue-500/50 transition-colors bg-white/5">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
            <Upload className="w-10 h-10 mx-auto text-blue-400" />
            <div className="text-sm font-medium text-gray-200">
              {file ? file.name : "Fai clic qui o trascina un file da analizzare"}
            </div>
            <p className="text-xs text-gray-500">I file caricati non abbandonano mai la memoria locale di questo computer</p>
          </label>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleUpload}
            disabled={loading || !file}
            className="px-6 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm disabled:opacity-50 transition-all shadow-lg shadow-blue-500/20"
            title="Esegue l'estrazione del testo e l'analisi automatica delle entità PII"
          >
            {loading ? "Elaborazione in corso..." : "Carica ed Esegui Scansione PII"}
          </button>
        </div>
      </div>

      {/* Detected Entities Table */}
      {entities.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">2. Entità Sensibili Rilevate ({entities.length})</h2>
              <p className="text-xs text-gray-400 mt-1">Elenco delle informazioni personali identificate dal motore di scansione</p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">
              Analisi Presidio + Gemma Vision OK
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/10 text-gray-400">
                  <th className="py-3 px-4">Tipo Entità</th>
                  <th className="py-3 px-4">Categoria</th>
                  <th className="py-3 px-4">Riconoscitore</th>
                  <th className="py-3 px-4">Confidenza</th>
                  <th className="py-3 px-4">Valore Cifrato (Hash)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-gray-300">
                {entities.map((e, idx) => (
                  <tr key={idx} className="hover:bg-white/5">
                    <td className="py-3 px-4 font-semibold text-blue-300">{e.entity_type}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        e.category === "PII_SPECIAL" ? "bg-red-500/20 text-red-300 border border-red-500/30" :
                        e.category === "PII_DIRECT" ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" :
                        "bg-blue-500/20 text-blue-300"
                      }`}>
                        {e.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-400">{e.detector}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400">{(e.confidence * 100).toFixed(0)}%</td>
                    <td className="py-3 px-4 font-mono text-gray-500 text-[10px]">{e.value_hash?.slice(0, 16)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Protection Strategy Selection & Vault */}
      {docData && (
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-white">3. Selezione Strategia di Protezione</h2>
            <p className="text-xs text-gray-400 mt-1">Scegli come trasformare i dati sensibili prima di inoltrarli in Zona 1</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div
              onClick={() => setStrategy("MASK")}
              className={`p-4 rounded-2xl cursor-pointer border transition-all ${
                strategy === "MASK" ? "bg-blue-600/20 border-blue-500 text-white" : "bg-white/5 border-white/10 text-gray-400 hover:border-white/20"
              }`}
            >
              <div className="font-bold text-sm text-blue-300 mb-1">MASK (Oscuramento)</div>
              <p className="text-gray-300">Sostituisce i dati personali con etichette generiche di tipo. Es: <code className="text-amber-300">[CODICE_FISCALE]</code>.</p>
            </div>

            <div
              onClick={() => setStrategy("REPLACE")}
              className={`p-4 rounded-2xl cursor-pointer border transition-all ${
                strategy === "REPLACE" ? "bg-purple-600/20 border-purple-500 text-white" : "bg-white/5 border-white/10 text-gray-400 hover:border-white/20"
              }`}
            >
              <div className="font-bold text-sm text-purple-300 mb-1">REPLACE (Vault Pseudonimizzazione)</div>
              <p className="text-gray-300">Crea token cifrati reversibili salvati nel Vault locale. Es: <code className="text-purple-300">PERSON_001</code>.</p>
            </div>

            <div
              onClick={() => setStrategy("GENERALIZE")}
              className={`p-4 rounded-2xl cursor-pointer border transition-all ${
                strategy === "GENERALIZE" ? "bg-emerald-600/20 border-emerald-500 text-white" : "bg-white/5 border-white/10 text-gray-400 hover:border-white/20"
              }`}
            >
              <div className="font-bold text-sm text-emerald-300 mb-1">GENERALIZE (Aggregazione)</div>
              <p className="text-gray-300">Riduce la precisione dei dati (es. fasce d'età o solo provincia invece dell'indirizzo completo).</p>
            </div>
          </div>

          {/* Optional Vault Passphrase */}
          {strategy === "REPLACE" && (
            <div className="p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 space-y-2">
              <label className="text-xs font-semibold text-purple-300 flex items-center gap-2">
                <Lock className="w-4 h-4" /> Passphrase Vault Personale (Opzionale)
              </label>
              <input
                type="password"
                placeholder="Inserisci la passphrase per cifrare il Vault (o lascia vuoto per la master key locale)"
                value={vaultPass}
                onChange={(e) => setVaultPass(e.target.value)}
                className="w-full px-4 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
              <p className="text-[11px] text-gray-400">Le mappe di pseudonimizzazione vengono cifrate con algoritmo PBKDF2 + AES-GCM 256 in Zona 0.</p>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={handleProtect}
              disabled={loading}
              className="px-6 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm disabled:opacity-50 transition-all shadow-lg shadow-emerald-500/20"
              title="Genera la versione protetta del documento per Zona 1"
            >
              {loading ? "Protezione in corso..." : "Applica Protezione e Valida"}
            </button>
          </div>
        </div>
      )}

      {/* Protection Results & Diff */}
      {protectResult && (
        <div className="glass-panel p-6 rounded-3xl space-y-6 border-emerald-500/30">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">4. Risultati della Protezione & Valutazione Punteggi</h2>
              <p className="text-xs text-gray-400 mt-1">Versione Generata: <code className="text-emerald-400">{protectResult.result_version_id}</code></p>
            </div>
            <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${
              protectResult.validator_pass ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" : "bg-red-500/20 text-red-300 border-red-500/30"
            }`}>
              {protectResult.validator_pass ? "Zero-Residue PASS ✅" : "Residuo Rilevato ⚠️"}
            </span>
          </div>

          {/* Operator File Status Note */}
          <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-xs text-gray-300 space-y-3">
            <div className="flex items-center justify-between">
              <div className="font-semibold text-blue-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Preservazione Documento & Nuova Versione Generata
              </div>
              <button
                onClick={handleDownload}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-emerald-500/20"
                title="Scarica il nuovo file bonificato mantenendo il formato del file originale"
              >
                <Download className="w-4 h-4" /> Scarica File Protetto ({protectResult.export_filename || "bonificato"})
              </button>
            </div>
            <p className="leading-relaxed">
              1. 🔒 <strong>File Originale Integro:</strong> Il file originale non viene modificato né sovrascritto. Rimane custodito inalterato in <strong>Zona 0 (Strict Local)</strong>.<br />
              2. 🛡️ <strong>Nuovo File Prodotto:</strong> È stato creato ed esportato il nuovo file <code>{protectResult.export_filename || "protetto"}</code> in <strong>Zona 1 (Internal Pipeline)</strong>.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-white/5 space-y-1">
              <span className="text-xs text-gray-400">Punteggio Privacy</span>
              <div className="text-2xl font-bold text-emerald-400">{protectResult.privacy_score}%</div>
              <p className="text-[10px] text-gray-500">Livello di protezione delle informazioni PII</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 space-y-1">
              <span className="text-xs text-gray-400">Punteggio Utilità</span>
              <div className="text-2xl font-bold text-blue-400">{protectResult.utility_score}%</div>
              <p className="text-[10px] text-gray-500">Preservazione della semantica per l'LLM</p>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 space-y-1">
              <span className="text-xs text-gray-400">Rischio Re-Identificazione</span>
              <div className="text-2xl font-bold text-amber-400">{(protectResult.reid_risk * 100).toFixed(1)}%</div>
              <p className="text-[10px] text-gray-500">Probabilità di ricombinazione indiretta</p>
            </div>
          </div>

          {/* Interactive Diff Viewer */}
          {diff.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-white">Registro Differenze Applicate ({diff.length})</h3>
              <div className="max-h-60 overflow-y-auto rounded-2xl bg-black/40 p-4 border border-white/10 space-y-2 text-xs">
                {diff.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between py-1 border-b border-white/5">
                    <span className="text-red-400 line-through font-mono">{item.original}</span>
                    <span className="text-gray-500 text-[10px]">➔</span>
                    <span className="text-emerald-400 font-mono font-bold">{item.replacement}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-white/10 text-gray-400">{item.entity_type}</span>
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
