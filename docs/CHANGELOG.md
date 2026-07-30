# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [1.0.0] - M6 Hardening, Benchmark, Pacchettizzazione & Consegna Finale (`m6-final-delivery`)

### Aggiunto
- **Script di Hardening della Sicurezza** ([verify_security_hardening.py](file:///c:/Users/info/Documents/Sentinell/scripts/verify_security_hardening.py)): Convalida automatizzata del binding `127.0.0.1`, isolamento Vault, assenza di PII nei log di audit, integrità della catena SHA256 ed egress allowlist.
- **Suite di Benchmark di Performance** ([run_benchmarks.py](file:///c:/Users/info/Documents/Sentinell/scripts/run_benchmarks.py)): Misurazione delle latenze dell'Anonymizer Engine ($< 150\text{ ms}$), Pre-flight Privacy Gate ($< 20\text{ ms}$), Hybrid Retrieval RRF ($< 50\text{ ms}$) ed esecuzione Rule Engine ($< 30\text{ ms}$), con salvataggio del report `docs/BENCHMARK_RESULTS.json`.
- **Pacchettizzatore Offline Air-Gapped** ([package_offline.py](file:///c:/Users/info/Documents/Sentinell/scripts/package_offline.py)): Generazione dello zip di distribuzione offline `dist/aigate_offline_v1.0.zip`.
- **Script di Avvio Rapido**: File di avvio automatico `start_aigate.bat` (Windows) e `start_aigate.sh` (Linux/macOS).
- **Manuali & Report di Consegna Finale**: [OFFLINE_DEPLOYMENT_GUIDE.md](file:///c:/Users/info/Documents/Sentinell/docs/OFFLINE_DEPLOYMENT_GUIDE.md) e [FINAL_DELIVERY_REPORT.md](file:///c:/Users/info/Documents/Sentinell/docs/FINAL_DELIVERY_REPORT.md).

---

## [0.5.0] - M5 Interfaccia Utente Desktop Local (`m5-desktop-ui`)

### Aggiunto
- Infrastruttura Next.js 14 App Router, Tailwind CSS, Framer Motion, Lucide Icons, Sonner. Client API TypeScript, estetica "The Apple Feel", 5 viste integrate (Dashboard 3 Zone, Privacy Center con Diff e Vault, Compliance Wizard con report cromatico, LLM Gateway Chat e Audit/ARKS Center).

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
