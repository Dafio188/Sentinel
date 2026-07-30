"use client";

import { useEffect, useState } from "react";
import { Cpu, Send, Lock, ShieldCheck, AlertTriangle, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function GatewayPage() {
  const [providers, setProviders] = useState<any[]>([]);
  const [selectedProvider, setSelectedProvider] = useState("ollama-local");
  const [promptText, setPromptText] = useState("");
  const [chatLog, setChatLog] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = () => {
    api.getProviders().then((res) => setProviders(res.providers || [])).catch(console.error);
  };

  const handleUpdatePrivacyClass = async (provId: string, currentClass: string) => {
    try {
      const nextClass = currentClass === "EXTERNAL" ? "TRUSTED" : "EXTERNAL";
      await api.updateProvider(provId, nextClass);
      toast.success(`Classe privacy per ${provId} aggiornata a ${nextClass}`);
      loadProviders();
    } catch (err: any) {
      toast.error(err.message || "Azione non consentita (Lock Attivo)");
    }
  };

  const handleSendChat = async () => {
    if (!promptText.trim()) return;

    const userMsg = { sender: "USER", text: promptText, time: new Date().toLocaleTimeString() };
    setChatLog((prev) => [...prev, userMsg]);
    setPromptText("");
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
        postflight_result: chatRes.postflight_result,
        reid_warning: chatRes.reid_warning,
        time: new Date().toLocaleTimeString(),
      };
      setChatLog((prev) => [...prev, botMsg]);
    } catch (err: any) {
      toast.error(err.message || "Richiesta bloccata dal Privacy Gate");
      setChatLog((prev) => [
        ...prev,
        {
          sender: "GATE",
          text: "⛔ Chiamata Bloccata dal Privacy Gate Pre-flight per motivi di conformità o PII in chiaro.",
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">LLM Router & Privacy Gate</h1>
        <p className="text-gray-400 mt-1">Matrice dei provider LLM, Pre-flight Data & Prompt Gate e Post-flight Scanner</p>
      </div>

      {/* LLM Provider Matrix */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-400" /> Matrice dei Provider Registrati
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {providers.map((p) => (
            <div
              key={p.id}
              onClick={() => setSelectedProvider(p.id)}
              className={`glass-card p-4 rounded-2xl cursor-pointer transition-all border ${
                selectedProvider === p.id ? "border-blue-500 bg-blue-500/10" : "border-white/10"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-white text-sm">{p.name}</span>
                {p.privacy_class_locked === 1 && (
                  <span title="Classe Privacy Bloccata">
                    <Lock className="w-4 h-4 text-red-400" />
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400 font-mono truncate">{p.endpoint}</p>

              <div className="mt-3 flex items-center justify-between pt-2 border-t border-white/5">
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                  p.privacy_class === 'LOCAL' ? 'bg-emerald-500/20 text-emerald-300' :
                  p.privacy_class === 'EXTERNAL' ? 'bg-blue-500/20 text-blue-300' : 'bg-red-500/20 text-red-300'
                }`}>
                  {p.privacy_class}
                </span>

                {p.privacy_class_locked === 0 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleUpdatePrivacyClass(p.id, p.privacy_class);
                    }}
                    className="text-[10px] text-gray-400 hover:text-white underline"
                  >
                    Modifica
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Pre-flight & Post-flight Chat */}
      <div className="glass-panel p-6 rounded-3xl space-y-4 flex flex-col h-[450px]">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-semibold text-white">Chat Gateway (Provider Selezionato: {selectedProvider})</h2>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Pre-flight Gate ATTIVO
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-2">
          {chatLog.length === 0 && (
            <div className="text-center py-12 text-gray-500 text-sm">
              Nessun messaggio inviato. Prova ad inviare una richiesta per testare il Privacy Gate.
            </div>
          )}

          {chatLog.map((msg, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-2xl max-w-xl text-sm ${
                msg.sender === "USER"
                  ? "ml-auto bg-blue-600/30 text-white border border-blue-500/30"
                  : msg.sender === "GATE"
                  ? "bg-red-500/20 text-red-300 border border-red-500/30"
                  : "bg-white/5 text-gray-200 border border-white/10"
              }`}
            >
              <div className="flex items-center justify-between text-[10px] opacity-60 mb-1">
                <span>{msg.sender}</span>
                <span>{msg.time}</span>
              </div>
              <p className="whitespace-pre-wrap">{msg.text}</p>
              {msg.postflight_result && (
                <div className="mt-2 pt-2 border-t border-white/10 text-[10px] flex items-center justify-between">
                  <span>Post-flight: {msg.postflight_result}</span>
                  {msg.reid_warning && <span className="text-amber-400 font-semibold">⚠️ Avviso Re-ID</span>}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="flex gap-3 pt-2">
          <input
            type="text"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
            placeholder="Scrivi un prompt per l'LLM..."
            className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSendChat}
            disabled={loading || !promptText.trim()}
            className="apple-button px-6 py-3 text-sm font-semibold flex items-center gap-2"
          >
            Invia <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
