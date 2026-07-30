# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [Unreleased] - M5 Interfaccia Utente Desktop Local (`m5-desktop-ui`)

### Aggiunto
- **Infrastruttura Frontend Next.js** ([frontend/](file:///c:/Users/info/Documents/Sentinell/frontend/)): Setup Next.js 14 App Router, Tailwind CSS, Framer Motion, Lucide Icons e Sonner per i toast notifiche.
- **Client API TypeScript** ([api.ts](file:///c:/Users/info/Documents/Sentinell/frontend/lib/api.ts)): Client per comunicare in locale con le API REST di AIGate su `http://127.0.0.1:8000/api`.
- **Layout & Estetica "The Apple Feel"** ([globals.css](file:///c:/Users/info/Documents/Sentinell/frontend/app/globals.css)): Glassmorphism (`backdrop-blur-xl`), squirkle radius, micro-interazioni spring physics, modalità OLED pure black ed interfaccia completamente in italiano.
- **Dashboard Principale** ([page.tsx](file:///c:/Users/info/Documents/Sentinell/frontend/app/page.tsx)): Widget delle 3 Zone di Sicurezza (0=RED, 1=AMBER, 2=GREEN), contatori documenti scansionati, badge di integrità dell'Audit Chain e stato dei servizi.
- **Privacy Center** ([privacy/page.tsx](file:///c:/Users/info/Documents/Sentinell/frontend/frontend/app/privacy/page.tsx)): Upload drag-and-drop, tabella entità PII con evidenziazione per categoria (`SPECIAL`, `IDENTIFIER`, `FINANCIAL`), selettore di strategia (`MASK`, `REPLACE`, `GENERALIZE`, `REMOVE`, `SEMANTIC`), visualizzatore Diff interattivo (originale vs protetto) e sblocco Vault con passphrase.
- **Compliance Wizard & Assessment** ([compliance/page.tsx](file:///c:/Users/info/Documents/Sentinell/frontend/app/compliance/page.tsx)): Wizard adattivo passo-passo con domande dinamiche, report per aree cromatiche (🟢/🟡/🟠/🔴/⚪) e albero interattivo della Compliance Chain Traversal.
- **LLM Gateway & Chat Interface** ([gateway/page.tsx](file:///c:/Users/info/Documents/Sentinell/frontend/app/gateway/page.tsx)): Matrice dei provider LLM con indicatore di blocco/lock su DeepSeek e verifica loopback per Ollama, chat con status Pre-flight Gate ed avvisi PII/HR in tempo reale.
- **Audit & ARKS Knowledge Center** ([audit/page.tsx](file:///c:/Users/info/Documents/Sentinell/frontend/app/audit/page.tsx)): Registro eventi di audit con pulsante "Verifica Integrità Catena" e gestore versioni KB (`KB-2026.07-A` e `KB-2026.07-B`) con pulsante di approvazione umana ("Conferma e Attiva").

---

## [0.4.0] - M4 ARKS + Compliance Engine (`m4-compliance-arks`)

### Aggiunto
- Knowledge Versions Seed (`KB-2026.07-A` e `KB-2026.07-B`), ingestione fonti e chunking EUR-Lex, Hybrid Retrieval RRF, 64 regole v0.1 in Rule DSL, question bank & wizard adattivo pesato per severità, assessment engine a doppia data e Compliance Chain Traversal.

---

## [0.3.0] - M3 LLM Router & Privacy Gate (`m3-router-gates`)

### Aggiunto
- Provider Registry con lock immodificabile per `deepseek` (403), connettori LLM, Policy Engine (`STRICT`, `BALANCED`, `CUSTOM`), Pre-flight Data & Prompt Gate con restrizioni GDPR Capo V / CH5, Post-flight Scanner e API REST.

---

## [0.2.0] - M2 Privacy Engine (`m2-privacy-engine`)

### Aggiunto
- Parser multi-formato con metadati, OCR Ibrido Tesseract + Gemma Vision, Analyzer Presidio, Anonymizer Engine, Zero-Residue Validator e Scoring.

---

## [0.1.0] - M1 Foundations (`m1-foundations`)

### Aggiunto
- Specifiche di progetto in `docs/`, architettura FastAPI `127.0.0.1`, SQLite DDL v0.1, Vault Argon2id/AES-GCM, Audit Chain crittografica e Rule DSL 3-valued.
