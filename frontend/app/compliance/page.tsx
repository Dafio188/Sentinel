"use client";

import { useState } from "react";
import { FileText, Plus, HelpCircle, CheckCircle2, AlertTriangle, ArrowRight, GitCommit } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function CompliancePage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<any>("");
  const [assessmentReport, setAssessmentReport] = useState<any>(null);
  const [complianceChain, setComplianceChain] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCreateProject = async () => {
    if (!projectName.trim()) return;
    setLoading(true);
    try {
      const p = await api.createProject({ name: projectName });
      setProjectId(p.id);
      toast.success("Progetto creato. Inizio Wizard Adattivo...");

      const next = await api.wizardNext(p.id);
      setCurrentQuestion(next.next_question);
    } catch (err: any) {
      toast.error(err.message || "Errore creazione progetto");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!projectId || !currentQuestion) return;
    setLoading(true);
    try {
      const next = await api.wizardNext(projectId, {
        question_id: currentQuestion.id,
        answer: selectedAnswer,
      });

      if (next.completed || !next.next_question) {
        toast.success("Wizard completato! Esecuzione Assessment...");
        const ass = await api.assessProject(projectId);
        const report = await api.getAssessmentReport(ass.assessment_id);
        setAssessmentReport(report);
        setCurrentQuestion(null);
      } else {
        setCurrentQuestion(next.next_question);
        setSelectedAnswer("");
      }
    } catch (err: any) {
      toast.error(err.message || "Errore risposta wizard");
    } finally {
      setLoading(false);
    }
  };

  const handleInspectChain = async (findingId: string) => {
    if (!assessmentReport) return;
    try {
      const chain = await api.getComplianceChain(assessmentReport.assessment_id, findingId);
      setComplianceChain(chain);
    } catch (err: any) {
      toast.error(err.message || "Errore durante il caricamento della Compliance Chain");
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Compliance Engine & Adaptive Wizard</h1>
        <p className="text-gray-400 mt-1">Valutazione di conformità AI Act & GDPR con Compliance Chain Traversal</p>
      </div>

      {/* Create Project Section */}
      {!projectId && (
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Plus className="w-5 h-5 text-blue-400" /> Nuovo Progetto di Conformità
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Inserisci il nome del progetto AI..."
              className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={handleCreateProject}
              disabled={loading}
              className="apple-button px-6 py-3 text-sm font-semibold"
            >
              Crea e Inizia Wizard
            </button>
          </div>
        </div>
      )}

      {/* Adaptive Wizard View */}
      {currentQuestion && (
        <div className="glass-panel p-8 rounded-3xl space-y-6 border-blue-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Domanda Wizard Adattivo</span>
            <span className="text-xs text-gray-400 font-mono">{currentQuestion.id}</span>
          </div>

          <h2 className="text-xl font-semibold text-white">{currentQuestion.text}</h2>

          <div className="space-y-3">
            {currentQuestion.options && currentQuestion.options.map((opt: string) => (
              <label
                key={opt}
                className={`flex items-center gap-3 p-4 rounded-2xl border cursor-pointer transition-all ${
                  selectedAnswer === opt
                    ? "bg-blue-600/20 border-blue-500 text-white"
                    : "bg-white/5 border-white/10 text-gray-300 hover:bg-white/10"
                }`}
              >
                <input
                  type="radio"
                  name="wizard_option"
                  value={opt}
                  checked={selectedAnswer === opt}
                  onChange={(e) => setSelectedAnswer(e.target.value)}
                  className="hidden"
                />
                <span className="font-medium text-sm">{opt}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleAnswerSubmit}
            disabled={!selectedAnswer || loading}
            className="apple-button w-full py-3 text-sm font-semibold flex items-center justify-center gap-2"
          >
            Conferma Risposta <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Chromatic Area Report & Findings */}
      {assessmentReport && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl flex items-center justify-between border-emerald-500/30">
            <div>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Esito Complessivo Assessment</span>
              <h2 className="text-2xl font-bold text-white mt-1">{assessmentReport.badge}</h2>
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-400">Versione KB Normativa</span>
              <p className="text-sm font-mono text-blue-400 font-semibold">{assessmentReport.kb_version}</p>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-3xl space-y-4">
            <h3 className="text-lg font-semibold text-white">Tessere di Conformità per Area</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {assessmentReport.findings && assessmentReport.findings.map((f: any) => (
                <div
                  key={f.id}
                  onClick={() => handleInspectChain(f.id)}
                  className="glass-card p-4 rounded-2xl cursor-pointer hover:border-blue-500/50 transition-all space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-gray-400">{f.rule_id}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      f.status === 'MET' ? 'bg-emerald-500/20 text-emerald-300' :
                      f.status === 'REVIEW' ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300'
                    }`}>
                      {f.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-200 font-medium line-clamp-2">{f.explanation}</p>
                  <div className="text-[10px] text-blue-400 flex items-center gap-1 font-semibold">
                    <GitCommit className="w-3 h-3" /> Ispeziona Compliance Chain
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Compliance Chain Traversal Modal/Panel */}
      {complianceChain && (
        <div className="glass-panel p-6 rounded-3xl space-y-4 border-blue-500/40 bg-blue-500/5">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="text-base font-semibold text-blue-400 flex items-center gap-2">
              <GitCommit className="w-5 h-5" /> Compliance Chain Traversal
            </h3>
            <button onClick={() => setComplianceChain(null)} className="text-xs text-gray-400 hover:text-white">
              Chiudi
            </button>
          </div>

          <div className="p-4 rounded-2xl bg-black/40 font-mono text-xs text-emerald-400">
            {complianceChain.chain_path}
          </div>

          <div className="space-y-2 text-xs">
            <p className="text-gray-300"><strong>Regola:</strong> {complianceChain.rule?.title || complianceChain.finding_id}</p>
            <p className="text-gray-400"><strong>Spiegazione RAG:</strong> {complianceChain.explanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
