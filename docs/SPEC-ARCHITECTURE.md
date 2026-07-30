# AIGate — Architecture Specification (SPEC-ARCHITECTURE.md)

## 1. Invarianti Non Negoziali (I1–I3)

### I1. Separazione fisica delle zone
Contenuti originali e vault pseudonimi (**ZONA 0**) non vivono nello stesso database dei dati di pipeline (**ZONA 1**). Nessun oggetto ZONA 0 può essere passato a un connettore esterno o a un gestore di egress.

### I2. Le richieste esterne referenziano, non contengono
`llm_requests` per provider esterni memorizza l'hash del payload + riferimento alla versione protetta. L'unico percorso originale → API esterna passa per un `anonymization_event` + esito `PASS` del Privacy Gate.

### I3. Audit append-only con hash chain
Ogni evento di audit include l'hash del record precedente (`prev_hash`). La manomissione di qualsiasi riga del registro rende invalida l'intera catena e dev'essere rilevabile da `verify()`.

---

## 2. Modello a 3 Zone di Sicurezza

- **ZONA 0 (Strict Local & Vault)**: Documenti originali (`documents/original`), Vault cifrato SQLCipher (`data/vault.db`), mappe di pseudonimizzazione originali. Mai esposta verso l'esterno o la pipeline standard.
- **ZONA 1 (Internal Pipeline & Protected Data)**: Documenti estratti, mascherati, pseudonimizzati o semanticamente generalizzati, database di supporto `aigate.db`, vettori locali.
- **ZONA 2 (External Egress)**: Payload inviati ai connettori esterni (es. OpenAI, Anthropic, Gemini, DeepSeek). Accessibile solo previa validazione e passaggio del Privacy Gate con esito `PASS`.

---

## 3. I 5 Livelli Architetturali

1. **Interface Layer**: React SPA (Vite + TS) in ascolto locale servita dal backend FastAPI.
2. **Orchestrator Layer**: Coordinator FastAPI locale (127.0.0.1) con gestione session token e autorizzazione a livello di endpoint.
3. **Privacy + Compliance Layer**: Privacy Engine (Presidio, spaCy, Gemma 4, OCR) + Policy Engine + Rule DSL 3-valued + ARKS (RAG).
4. **AI Engine Layer**: Connettore Ollama locale + connettori LLM esterni controllati da Egress Allowlist.
5. **Storage Layer**: SQLite (`data/aigate.db`), SQLCipher (`data/vault.db`), `vectors/vec.db` e filesystem protetto con permessi ristretti.

---

## 4. I 3 Gate di Protezione

- **Data Gate**: Blocca l'invio di dati non protetti o non conformi al Capo V GDPR verso provider non locali/non adeguati.
- **Prompt Gate**: Analizza i prompt utente per rilevare PII o tentativi di identificazione non autorizzati prima della trasmissione.
- **Project Gate**: Valuta i parametri di progetto rispetto a GDPR e AI Act tramite il Rule Engine deterministico.

---

## 5. Le 4 Aree UI (React SPA)

1. **Privacy**: Ingestion, scansione PII, override entità, anonimizzazione (MASK/REPLACE/GENERALIZE/SEMANTIC), diff viewer e dialog Privacy Check.
2. **AI Workspace**: Chat con LLM locale ed esterni, allegato versioni protette, indicatori pre/post-flight.
3. **Compliance**: Wizard adattivo per progetti AI, valutazione GDPR/AI Act con doppia data (oggi vs deploy), Compliance Chain e spiegazioni RAG.
4. **Test di attacco**: Suite avversariale (Red Team) per misurare la robustezza dell'anonimizzazione e verificare i tentativi di prompt injection.
