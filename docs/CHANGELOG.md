# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [Unreleased] - M3 LLM Router & Privacy Gate (`m3-router-gates`)

### Aggiunto
- **Provider Registry** ([registry.py](file:///c:/Users/info/Documents/Sentinell/backend/app/llm/registry.py)): Seed dei 5 provider, lock enforcement su `privacy_class_locked` per `deepseek` (403), verifica automatica dell'IP loopback per Ollama e gestione del tier Gemini (`FREE` trattato come `UNKNOWN`).
- **Connettori LLM Sicuri** ([connectors/](file:///c:/Users/info/Documents/Sentinell/backend/app/llm/connectors/)): Connettore Ollama locale con `num_ctx` esplicito e connettori esterni trasparenti operanti tramite la allowlist egress di `GuardedHttpClient`.
- **Policy Engine** ([policy.py](file:///c:/Users/info/Documents/Sentinell/backend/app/gate/policy.py)): Valutatore delle policy `STRICT`, `BALANCED` e `CUSTOM`.
- **Pre-flight Data & Prompt Gate** ([preflight.py](file:///c:/Users/info/Documents/Sentinell/backend/app/gate/preflight.py)):
  - Invariante I2: Blocco `EXTRACTED` verso provider non-LOCAL.
  - Controllo `CROSS-02` per PII nel prompt o payload pseudonimizzati.
  - Applicazione delle restrizioni sui trasferimenti extra-UE (GDPR Capo V / CH5 per DeepSeek).
  - Rilevamento prompt avversariali o identificazioni personali legate a valutazioni HR (es. "Mario Rossi").
  - Persistenza in `llm_requests` con rispetto del vincolo `CHECK`.
- **Chiamata + Post-flight Scanner** ([postflight.py](file:///c:/Users/info/Documents/Sentinell/backend/app/gate/postflight.py)): Scansione risposte LLM per PII in chiaro (`LEAK_SUSPECT`) ed euristica di re-identificazione v1 (`REID_WARNING`).
- **API REST Gateway** ([router.py](file:///c:/Users/info/Documents/Sentinell/backend/app/api/router.py)): Endpoints `GET/PATCH /providers`, `POST /gate/preflight`, `POST /chat` e `GET /requests/{id}`.
- **Suite di Test M3** ([test_m3_router_gates.py](file:///c:/Users/info/Documents/Sentinell/backend/tests/test_m3_router_gates.py)): 8 test di accettazione automatizzati per la Definition of Done della M3.

---

## [0.2.0] - M2 Privacy Engine (`m2-privacy-engine`)

### Aggiunto
- Parser multi-formato (DOCX, PDF, TXT, CSV, XLSX, immagini) con estrazione metadati.
- OCR Ibrido Tesseract + Gemma Vision con cross-check anti-allucinazione.
- Analyzer Presidio con recognizer italiani e validazione checksum.
- Pass Semantico Gemma con riallineamento quote anti-allucinazione.
- Merge Engine, Anonymizer Engine (MASK, REPLACE, GENERALIZE, REMOVE, SEMANTIC), Zero-Residue Validator, Scoring e API REST.

---

## [0.1.0] - M1 Foundations (`m1-foundations`)

### Aggiunto
- Deposito delle specifiche di progetto in `docs/` (`SPEC-ARCHITECTURE.md`, `SPEC-DDL.sql`, `SPEC-RULES-DSL.md`, `SPEC-PROVIDERS.md`, `CHANGELOG.md`).
- Architettura base backend Python 3.12 / FastAPI blindato su `127.0.0.1`.
- Database SQLite `data/aigate.db` con schema DDL v0.1.
- Vault cifrato `data/vault.db` con derivazione Argon2id / PBKDF2 e cifratura AES-GCM 256.
- Registro Audit Append-Only con Catena Crittografica Hash-Chain.
- Modello a 3 Zone di Sicurezza con decoratore `@requires_zone_max`.
- Client HTTP con Allowlist Egress.
- Valutatore DSL Three-Valued Logic.
