"use client";

import { useEffect, useState } from "react";
import { Send, Shield, Lock, Unlock, Server, Bot, AlertTriangle, CheckCircle, Info, HelpCircle } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function GatewayPage() {
  const [providers, setProviders] = useState<any[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>("ollama-local");
  const [prompt, setPrompt] = useState("");
  const [chatLog, setChatLog] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(true);

  useEffect(() => {
    api.getProviders().then((res) => {
      setProviders(res.providers || []);
    }).catch(console.error);
  }, []);

  const handleSendChat = async () => {
    if (!prompt.trim()) return;
    const userMsg = { sender: "USER", text: prompt, time: new Date().toLocaleTimeString() };
    setChatLog((prev) => [...prev, userMsg]);
    setPrompt("");
    setLoading(true);

    try {
      const chatRes = await api.chat({
        provider_id: selectedProvider,
        prompt_text: userMsg.text,
      });

      const botMsg = {
        sender: "LLM",
        text: chatRes.response_text,
        gate_result: chatRes.gate_result,
        postflight: chatRes.postflight_result,
        reid_warning: chatRes.reid_warning,
        time: new Date().toLocaleTimeString(),
      };
      setChatLog((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errMsg = err.message || "Richiesta bloccata dal Privacy Gate o errore di connessione";
      toast.error(errMsg);
      setChatLog((prev) => [
        ...prev,
        {
          sender: "GATE",
          text: `⛔ ${errMsg}`,
          gate_result: "BLOCK",
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">LLM Gateway & Privacy Gate</h1>
          <p className="text-gray-400 mt-1">Interfaccia di comunicazione protetta verso modelli locali ed esterni con scanner pre e post-flight</p>
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
        <div className="glass-panel p-6 rounded-3xl border-blue-500/30 bg-blue-500/5 space-y-3">
          <div className="flex items-center gap-2 text-blue-300 font-semibold text-sm">
            <Info className="w-5 h-5" /> Guida Operativa per la Comunicazione Sicura con gli LLM
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-300">
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-blue-300">1. Selezione Provider</span>
              <p className="text-gray-400">Scegli tra <strong>Ollama Local</strong> (locale su questo PC) o modelli esterni. I modelli esterni richiedono dati sanitizzati o anonimizzati.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-blue-300">2. Pre-flight Gate</span>
              <p className="text-gray-400">Prima di inviare il messaggio, il gate valuta il testo. In caso di PII o valutazioni HR su individui, la chiamata viene bloccata o filtrata.</p>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 space-y-1">
              <span className="font-semibold text-blue-300">3. Post-flight Scanner</span>
              <p className="text-gray-400">La risposta generata dall'LLM viene analizzata per prevenire la fuga accidentale di informazioni o tentativi di re-identificazione.</p>
            </div>
          </div>
        </div>
      )}

      {/* Provider Selection Matrix */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-white">Matrice dei Provider & Classi di Privacy</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {providers.map((p) => (
            <div
              key={p.id}
              onClick={() => setSelectedProvider(p.id)}
              className={`p-5 rounded-3xl cursor-pointer border transition-all space-y-2 ${
                selectedProvider === p.id
                  ? "glass-panel border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                  : "glass-card hover:border-white/20"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white">{p.name}</span>
                {p.privacy_class_locked === 1 && (
                  <span title="Classe di privacy bloccata da normativa del Garante">
                    <Lock className="w-4 h-4 text-red-400" />
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full border ${
                  p.privacy_class === "LOCAL" ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" :
                  p.privacy_class === "TRUSTED" ? "bg-blue-500/20 text-blue-300 border-blue-500/30" :
                  p.privacy_class === "EXTERNAL" ? "bg-amber-500/20 text-amber-300 border-amber-500/30" :
                  "bg-red-500/20 text-red-300 border-red-500/30"
                }`}>
                  {p.privacy_class}
                </span>

                {p.endpoint_verified_local === 1 && (
                  <span className="text-[10px] text-emerald-400 font-mono font-bold">127.0.0.1 ✅</span>
                )}
              </div>

              <p className="text-[11px] text-gray-400 font-mono truncate">{p.model}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Terminal */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-3">
            <Server className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-base font-bold text-white">Terminal Chat Protetto</h3>
              <p className="text-xs text-gray-400">Provider selezionato: <code className="text-blue-400 font-bold">{selectedProvider}</code></p>
            </div>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Privacy Gate ATTIVO
          </span>
        </div>

        {/* Messages List */}
        <div className="min-h-80 max-h-96 overflow-y-auto space-y-4 p-4 rounded-2xl bg-black/40 border border-white/5">
          {chatLog.length === 0 ? (
            <div className="text-center text-xs text-gray-500 py-12">
              Scrivi un messaggio sotto per avviare la comunicazione protetta con l'LLM.
            </div>
          ) : (
            chatLog.map((m, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-2xl space-y-1 text-xs ${
                  m.sender === "USER"
                    ? "bg-blue-600/10 border border-blue-500/20 ml-12 text-blue-100"
                    : m.sender === "GATE"
                    ? "bg-red-500/10 border border-red-500/30 text-red-200"
                    : "bg-white/5 border border-white/10 mr-12 text-gray-200"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-gray-400">
                  <span className="font-bold uppercase tracking-wider">{m.sender}</span>
                  <span>{m.time}</span>
                </div>
                <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                {m.postflight && (
                  <div className="pt-2 text-[10px] text-emerald-400 font-mono">
                    Post-flight Scan: {m.postflight} {m.reid_warning && "⚠️ Rischio Re-ID Rilevato"}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Input Bar */}
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Scrivi il tuo prompt qui (es. Riassumi queste indicazioni operative)..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
            className="flex-1 px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-xs"
          />
          <button
            onClick={handleSendChat}
            disabled={loading || !prompt.trim()}
            className="px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs disabled:opacity-50 transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20"
            title="Invia il prompt all'LLM previa valutazione del Privacy Gate"
          >
            <Send className="w-4 h-4" /> {loading ? "Valutazione..." : "Invia"}
          </button>
        </div>
      </div>
    </div>
  );
}
