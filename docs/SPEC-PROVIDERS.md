# AIGate — Provider Matrix Specification (SPEC-PROVIDERS.md)

## Matrice dei Provider LLM

| ID Provider | Classe Privacy | Paese | Meccanismo Trasferimento | Note & Vincoli Egress |
|---|---|---|---|---|
| `ollama-local` | `LOCAL` | — | N.A. | Endpoint DEVE risolvere su loopback (`127.0.0.0/8`, `::1`); `num_ctx` esplicito obbligatorio |
| `anthropic` | `EXTERNAL` | US | DPF / SCC | No training su dati API di default; richiede DPA attivo |
| `openai` | `EXTERNAL` | US | DPF / SCC | No training su dati API di default; richiede DPA attivo |
| `gemini` | `EXTERNAL` | US | DPF / SCC | Tier `PAID` ≠ `FREE`. Il tier `FREE` viene trattato come `UNKNOWN` dal Gate |
| `deepseek` | `UNKNOWN` (locked) | CN | NONE | Provvedimento Garante vigente. Accetta SOLO output `MASKED` / `SEMANTIC` con validator PASS e `reid_risk` LOW. Mai `REPLACE` o `EXTRACTED` |

---

## Vincoli Immodificabili (Locked Privacy Class)
Se `privacy_class_locked = 1` (es. provider `deepseek`), la classe di privacy del provider non è modificabile da UI o file di configurazione. Qualsiasi tentativo di patch o modifica restituisce un errore HTTP 403.

---

## Controllo Loopback per Provider Locali
Allo startup e a ogni modifica di endpoint per provider con classe `LOCAL`, il sistema effettua il bilanciamento/risoluzione DNS dell'host:
Se non risolve esclusivamente su indirizzi di loopback (`127.0.0.1`, `::1`), la classe di privacy viene degradata automaticamente a `EXTERNAL` / `UNKNOWN` e l'endpoint viene marcato come `endpoint_verified_local = 0`.
