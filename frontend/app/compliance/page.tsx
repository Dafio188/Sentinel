"use client";

import { useState } from "react";
import { Scale, FileCheck, CheckCircle2, AlertOctagon, HelpCircle, Info, ChevronRight, GitBranch, Download } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function CompliancePage() {
  const [projName, setProjName] = useState("");
  const [projPurpose, setProjPurpose] = useState("");
  const [projectId, setProjectId] = useState<string | null>(null);

  const [currentQ, setCurrentQ] = useState<any>(null);
  const [wizardCompleted, setWizardCompleted] = useState(false);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  const [assessment, setAssessment] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [selectedFindingChain, setSelectedFindingChain] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(true);
  const [dateInput, setDateInput] = useState<string>(new Date().toISOString().split("T")[0]);

  const [extractedFeatures, setExtractedFeatures] = useState<Record<string, any>>({});

  const handleCreateProject = async () => {
    if (!projName) return toast.error("Inserisci un nome per il progetto");
    setLoading(true);
    try {
      const proj = await api.createProject({
        name: projName,
        intended_purpose: projPurpose,
      });
      setProjectId(proj.id);
      if (proj.extracted_features && Object.keys(proj.extracted_features).length > 0) {
        setExtractedFeatures(proj.extracted_features);
        toast.info("🤖 AI Auto-Extraction: Parametri del progetto analizzati ed estratti automaticamente dal testo!");
      } else {
        toast.success("Progetto creato con successo!");
      }

      // Start wizard
      const wiz = await api.wizardNext(proj.id);
      if (wiz.completed) {
        setWizardCompleted(true);
        setCurrentQ(null);
        toast.success("Tutti i parametri sono stati pre-estratti dall'AI! Generazione del report legale in corso...");

        const assRes = await api.assessProject(proj.id);
        setAssessment(assRes);
        const repRes = await api.getAssessmentReport(assRes.assessment_id);
        setReport(repRes);
      } else {
        setCurrentQ(wiz.next_question);
      }
    } catch (err: any) {
      toast.error(err.message || "Errore nella creazione progetto");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerQuestion = async (value: any) => {
    if (!projectId || !currentQ) return;
    setLoading(true);
    try {
      const wiz = await api.wizardNext(projectId, {
        question_id: currentQ.id,
        answer: value,
      });
      setAnswers((prev) => ({ ...prev, [currentQ.id]: value }));

      if (wiz.completed) {
        setWizardCompleted(true);
        setCurrentQ(null);
        toast.success("Wizard completato! Esecuzione della valutazione legale...");

        // Auto assess
        const assRes = await api.assessProject(projectId);
        setAssessment(assRes);

        // Get chromatic report
        const repRes = await api.getAssessmentReport(assRes.assessment_id);
        setReport(repRes);
      } else {
        setCurrentQ(wiz.next_question);
      }
    } catch (err: any) {
      toast.error(err.message || "Errore durante il salvataggio della risposta");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadChain = async (findingId: string) => {
    if (!assessment) return;
    try {
      const chain = await api.getComplianceChain(assessment.assessment_id, findingId);
      setSelectedFindingChain(chain);
    } catch (err: any) {
      toast.error("Errore nel caricamento della catena di tracciabilità");
    }
  };

  const handleDownloadReport = () => {
    if (!report) return toast.error("Nessun report disponibile per il download");
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `sentinell_compliance_report_${projectId || "audit"}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    toast.success("Report di Compliance scaricato con successo!");
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Compliance Engine & ARKS</h1>
          <p className="text-gray-400 mt-1">Valutazione di conformità legale (GDPR Capo V + EU AI Act) basata su regole deterministiche a 3 valori</p>
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className="flex items-center gap-2 px-4 py-2 rounded-2xl glass-card text-xs font-semibold text-blue-400 hover:text-white"
        >
          <HelpCircle className="w-4 h-4" /> {showHelp ? "Nascondi Guida Operatore" : "Guida Operatore"}
        </button>
      </div>

      {/* Operator Instruction Box */}
      {showHelp && (
        <div className="glass-panel p-6 rounded-3xl border-emerald-500/30 bg-emerald-500/5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-300 font-semibold text-sm">
            <Info className="w-5 h-5" /> Guida Operativa all'Audit di Conformità Legale
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-gray-300">
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">1. Registra il Progetto</span>
              <p className="text-gray-400">Inserisci il nome del sistema AI ed il suo scopo operativo (es. Valutazione Lista Clienti con OpenAI).</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">2. Rispondi al Wizard</span>
              <p className="text-gray-400">Rispondi alle domande guidate. L'algoritmo calcola le priorità in base alla severità del rischio.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">3. Leggi il Report Cromatico</span>
              <p className="text-gray-400">Visualizza le 5 aree cromatiche (🟢/🟡/🟠/🔴/⚪) senza percentuali numeriche ingannevoli.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-emerald-300">4. Risali alla Legge (Chain)</span>
              <p className="text-gray-400">Fai clic su qualsiasi violazione per esplorare l'albero di tracciabilità fino all'articolo EUR-Lex originale.</p>
            </div>
          </div>
        </div>
      )}

      {/* Step 1: Create Project */}
      {!projectId && (
        <div className="glass-panel p-8 rounded-3xl space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-white">1. Registrazione Nuovo Progetto AI</h2>
            <p className="text-xs text-gray-400 mt-1">Crea la scheda del sistema AI per avviare l'analisi di conformità</p>
          </div>

          <div className="space-y-4 max-w-xl text-xs">
            <div>
              <label className="block text-gray-300 font-semibold mb-1">Nome del Sistema AI *</label>
              <input
                type="text"
                placeholder="Es. Valutazione Lista Clienti & Fatturato con OpenAI"
                value={projName}
                onChange={(e) => setProjName(e.target.value)}
                className="w-full px-4 py-2.5 rounded-2xl bg-black/40 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 text-xs"
              />
            </div>

            <div>
              <label className="block text-gray-300 font-semibold mb-1">Finalità Intesa (Intended Purpose)</label>
              <textarea
                placeholder="Es. Elaborazione lista clienti e calcolo fatturato tramite modello OpenAI esterno"
                value={projPurpose}
                onChange={(e) => setProjPurpose(e.target.value)}
                rows={3}
                className="w-full px-4 py-2.5 rounded-2xl bg-black/40 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 text-xs"
              />
            </div>

            <button
              onClick={handleCreateProject}
              disabled={loading || !projName}
              className="px-6 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm disabled:opacity-50 transition-all shadow-lg shadow-emerald-500/20"
            >
              {loading ? "Creazione in corso..." : "Avvia Wizard di Conformità"}
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Adaptive Wizard */}
      {projectId && !wizardCompleted && (
        <div className="space-y-4">
          {Object.keys(extractedFeatures).length > 0 && (
            <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-xs space-y-2">
              <div className="font-bold text-blue-300 flex items-center gap-2">
                <span>🤖 AI Auto-Ingestion & Extraction</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-200">Parametri Rilevati dal Testo</span>
              </div>
              <p className="text-gray-300 text-[11px]">
                Analizzando il nome ed il testo del progetto, il motore ha già pre-compilato ed auto-configurato i seguenti parametri:
              </p>
              <div className="flex flex-wrap gap-2 pt-1 font-mono text-[10px]">
                {extractedFeatures.domain && (
                  <span className="px-2.5 py-1 rounded bg-white/10 text-emerald-300 border border-emerald-500/30">
                    Dominio: <strong>{extractedFeatures.domain === "employment" ? "Risorse Umane (Employment)" : extractedFeatures.domain}</strong>
                  </span>
                )}
                {extractedFeatures.purpose && (
                  <span className="px-2.5 py-1 rounded bg-white/10 text-emerald-300 border border-emerald-500/30">
                    Finalità: <strong>{extractedFeatures.purpose === "recruitment" ? "Reclutamento / Selezione" : extractedFeatures.purpose}</strong>
                  </span>
                )}
                {extractedFeatures.is_ai_system && (
                  <span className="px-2.5 py-1 rounded bg-white/10 text-blue-300 border border-blue-500/30">
                    Sistema AI: <strong>SÌ (Model LLM / AI)</strong>
                  </span>
                )}
                {extractedFeatures.role && (
                  <span className="px-2.5 py-1 rounded bg-white/10 text-purple-300 border border-purple-500/30">
                    Ruolo: <strong>Deployer (Utilizzo API Esterna)</strong>
                  </span>
                )}
                {extractedFeatures.data_types && (
                  <span className="px-2.5 py-1 rounded bg-white/10 text-amber-300 border border-amber-500/30">
                    Dati: <strong>{extractedFeatures.data_types.join(", ")}</strong>
                  </span>
                )}
              </div>
            </div>
          )}

          {currentQ && (
            <div className="glass-panel p-8 rounded-3xl space-y-6 border-blue-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-blue-500/20 text-blue-300 font-bold uppercase">
                    Domanda Ponderata — Rischio {currentQ.weight >= 4 ? "CRITICO" : currentQ.weight >= 3 ? "ALTO" : "MEDIO"}
                  </span>
                  <h2 className="text-lg font-bold text-white mt-3">
                    {currentQ.text || currentQ.prompt || currentQ.title || `Q: ${currentQ.id}`}
                  </h2>
                </div>
                <span className="text-xs text-gray-400 font-mono">ID: <code className="text-blue-400">{currentQ.id}</code></span>
              </div>

          {/* Render Options with Rich Details or Date Picker */}
          {currentQ.answer_type === "DATE" || currentQ.id === "Q_DEPLOY_DATE" ? (
            <div className="space-y-4 pt-2">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <input
                  type="date"
                  value={dateInput}
                  onChange={(e) => setDateInput(e.target.value)}
                  className="px-4 py-3 rounded-2xl bg-black/50 border border-white/20 text-white font-mono text-sm focus:outline-none focus:border-blue-500 flex-1"
                />
                <button
                  onClick={() => handleAnswerQuestion(dateInput || new Date().toISOString().split("T")[0])}
                  disabled={loading}
                  className="px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition-all shadow-md shadow-blue-500/20"
                >
                  Conferma Data Deployment
                </button>
                <button
                  onClick={() => {
                    const today = new Date().toISOString().split("T")[0];
                    setDateInput(today);
                    handleAnswerQuestion(today);
                  }}
                  disabled={loading}
                  className="px-6 py-3 rounded-2xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 font-bold text-xs transition-all"
                >
                  Oggi (Già in Produzione)
                </button>
              </div>
              <p className="text-[11px] text-gray-400">
                La data di deployment determina se gli obblighi differiti dell'EU AI Act (es. 2026/2027) sono già vincolanti o meno per il sistema.
              </p>
            </div>
          ) : currentQ.options_detail && currentQ.options_detail.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
              {currentQ.options_detail.map((opt: any) => (
                <button
                  key={opt.value}
                  onClick={() => handleAnswerQuestion(opt.value)}
                  disabled={loading}
                  className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/50 text-left transition-all hover:bg-blue-600/10 space-y-1.5 group"
                >
                  <div className="font-bold text-xs text-blue-300 group-hover:text-white flex items-center gap-2">
                    <span>➔ {opt.label}</span>
                    <span className="text-[10px] font-mono text-gray-500 font-normal">({opt.value})</span>
                  </div>
                  {opt.desc && <p className="text-[11px] text-gray-400 leading-relaxed">{opt.desc}</p>}
                </button>
              ))}
            </div>
          ) : currentQ.options && currentQ.options.length > 0 && !currentQ.options.includes("YES") ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
              {currentQ.options.map((opt: string) => (
                <button
                  key={opt}
                  onClick={() => handleAnswerQuestion(opt)}
                  disabled={loading}
                  className="py-3 px-4 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/50 text-gray-200 font-semibold text-xs text-left transition-all hover:bg-blue-600/10"
                >
                  ➔ {opt}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex gap-4 pt-2">
              <button
                onClick={() => handleAnswerQuestion("YES")}
                disabled={loading}
                className="flex-1 py-3 rounded-2xl bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 font-bold text-sm hover:bg-emerald-600/30 transition-all"
                title="Seleziona SÌ se la condizione descritta si applica al tuo sistema"
              >
                SÌ / CONFERMATO
              </button>
              <button
                onClick={() => handleAnswerQuestion("NO")}
                disabled={loading}
                className="flex-1 py-3 rounded-2xl bg-red-600/20 border border-red-500/40 text-red-300 font-bold text-sm hover:bg-red-600/30 transition-all"
                title="Seleziona NO se la condizione non è presente nel tuo sistema"
              >
                NO / NON PRESENTE
              </button>
            </div>
          )}
            </div>
          )}
        </div>
      )}

      {/* Step 3: Chromatic Assessment Report */}
      {report && (
        <div className="space-y-6">
          <div className="glass-panel p-8 rounded-3xl space-y-6 border-emerald-500/30">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Report di Valutazione Legale</h2>
                <p className="text-xs text-gray-400 mt-1">Conformità deterministica GDPR Capo V + AI Act (Base Normativa: {report.kb_version})</p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleDownloadReport}
                  className="px-4 py-2 rounded-2xl bg-blue-600/20 border border-blue-500/40 hover:bg-blue-600/30 text-blue-300 font-semibold text-xs flex items-center gap-2 transition-all"
                  title="Scarica il certificato ed il report di audit completo in formato JSON"
                >
                  <Download className="w-4 h-4" />
                  <span>Scarica Audit Report</span>
                </button>
                <span className={`text-xs px-4 py-1.5 rounded-full font-bold border ${
                  report.overall_status === "NON_COMPLIANT" ? "bg-red-500/20 text-red-400 border-red-500/40" :
                  report.overall_status === "REQUIRES_HUMAN_REVIEW" ? "bg-amber-500/20 text-amber-300 border-amber-500/40" :
                  "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                }`}>
                  {report.badge}
                </span>
              </div>
            </div>

            {/* Findings List */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-white">Esiti di Conformità Rilevati ({report.findings.length})</h3>
              <div className="space-y-2">
                {report.findings.map((f: any, idx: number) => (
                  <div
                    key={idx}
                    onClick={() => handleLoadChain(f.id)}
                    className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/40 cursor-pointer transition-all flex items-center justify-between group"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full ${
                          f.color_code === "RED" || f.status === "NOT_MET" ? "bg-red-500" :
                          f.color_code === "AMBER" || f.status === "REVIEW" ? "bg-amber-500" :
                          "bg-emerald-500"
                        }`} />
                        <span className="font-bold text-xs text-white group-hover:text-blue-300 transition-colors">{f.title || f.rule_id}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-gray-400">{f.severity || "MEDIUM"}</span>
                        <span className="text-[10px] font-mono text-gray-500">({f.rule_id})</span>
                      </div>
                      <p className="text-xs text-gray-400 pl-4">{f.action_required || f.explanation || "Nessun intervento richiesto"}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Compliance Chain Traversal Tree */}
          {selectedFindingChain && (
            <div className="glass-panel p-6 rounded-3xl space-y-4 border-blue-500/30">
              <div className="flex items-center gap-2">
                <GitBranch className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Compliance Chain Traversal (Albero di Tracciabilità Legale)</h3>
              </div>

              <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-3 text-xs font-mono">
                <div className="text-red-400 font-bold">1. Esito finale: {selectedFindingChain.verdict}</div>
                <div className="text-amber-300 pl-4">➔ Azione Richiesta: {selectedFindingChain.action}</div>
                <div className="text-gray-200 pl-8">➔ Regola Applicata: <span className="font-bold text-white">{selectedFindingChain.rule_title || selectedFindingChain.rule_id}</span> ({selectedFindingChain.rule_id})</div>
                <div className="text-emerald-400 pl-12">
                  ➔ Riferimento Normativo EUR-Lex: <code className="bg-emerald-500/20 px-2.5 py-1 rounded text-emerald-300 border border-emerald-500/30">{selectedFindingChain.source_article}</code>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
