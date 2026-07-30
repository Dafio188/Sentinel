# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [Unreleased] - M2 Privacy Engine (`m2-privacy-engine`)

### Aggiunto
- **Parser multi-formato** ([parsers/](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/parsers/)): Parser per DOCX, PDF, TXT, CSV, XLSX e immagini con estrazione metadati come entità `METADATA` (autore, lastModifiedBy, commenti, GPS EXIF).
- **OCR Ibrido** ([ocr.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/ocr.py)): Tesseract + Gemma Vision con cross-check anti-allucinazione e flag `UNCERTAIN_PII`.
- **Analyzer deterministico Presidio** ([recognizers.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/recognizers.py), [analyzer.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/analyzer.py)): Recognizers italiani custom con validazione dei checksum per Codice Fiscale, Partita IVA, IBAN, PEC, Telefoni, Targhe, CIE, Tessera Sanitaria, Indirizzi, Matricole, Nomi/Cognomi, Dati Particolari (`SPECIAL`) e Dati Finanziari (`FINANCIAL`).
- **Pass Semantico Gemma** ([llm_detector.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/llm_detector.py)): Rilevamento di identificazioni indirette con riallineamento delle quote anti-allucinazione.
- **Merge Engine** ([merge.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/merge.py)): Precedenza deterministica per severità categoria (`SPECIAL` > `IDENTIFIER` > `FINANCIAL` > `INDIRECT`) e affidabilità detector.
- **Anonymizer Engine** ([anonymizer.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/anonymizer.py), [generalize.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/generalize.py)): Strategie `MASK`, `REPLACE` (Vault-backed), `GENERALIZE`, `REMOVE` e `SEMANTIC` con fallback automatico a `MASK`.
- **Zero-Residue Validator** ([validator.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/validator.py)): Scansione deterministica per garantire l'assenza di PII residue nel testo protetto.
- **Scoring & Privacy Snapshot** ([scores.py](file:///c:/Users/info/Documents/Sentinell/backend/app/privacy/scores.py)): Calcolo di `privacy_score`, `utility_score`, `reid_risk` e snapshot JSON.
- **API REST Privacy Engine** ([router.py](file:///c:/Users/info/Documents/Sentinell/backend/app/api/router.py)): Endpoints `POST /documents`, `POST /documents/{id}/scan`, `POST /documents/{id}/protect`, `GET /documents/{id}/versions`, `GET /versions/{id}/diff`.
- **Suite di Test M2** ([test_m2_privacy_engine.py](file:///c:/Users/info/Documents/Sentinell/backend/tests/test_m2_privacy_engine.py)): 7 test di accettazione per la Definition of Done della M2.

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
