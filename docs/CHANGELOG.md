# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [Unreleased] - M4 ARKS + Compliance Engine (`m4-compliance-arks`)

### Aggiunto
- **Knowledge Versions Seed**: Pre-popolamento delle versioni `KB-2026.07-A` (AI Act baseline + GDPR) e `KB-2026.07-B` (AI Act post-Omnibus attiva di default con le date di efficacia progressive dell'Art. 50, NCII, Annex III e Annex I).
- **Ingestione Fonti & Chunking EUR-Lex** ([ingest.py](file:///c:/Users/info/Documents/Sentinell/backend/app/arks/ingest.py)): Strutturazione dei chunk per articolo/comma (`{FRAMEWORK}_ART{n}_{seq}`) e file `scripts/fetch_sources.md` con le fonti ufficiali.
- **Retrieval Ibrido BM25 + Vector RRF** ([retrieval.py](file:///c:/Users/info/Documents/Sentinell/backend/app/arks/retrieval.py)): Retrieval ibrido con filtri temporali per data di efficacia e versione KB.
- **Inventario Regole v0.1 in Rule DSL** ([knowledge/rules/](file:///c:/Users/info/Documents/Sentinell/knowledge/rules/)): Regole GDPR, AI Act post-Omnibus e Cross-Framework in formato JSON JsonLogic 3-valued.
- **Question Bank & Wizard Adattivo Pesato** ([wizard.py](file:///c:/Users/info/Documents/Sentinell/backend/app/compliance/wizard.py)): 14 domande seed con selezione deterministica basata sulla severità delle regole (`CRITICAL`=4, `HIGH`=3, `MED`=2, `LOW`=1).
- **Assessment Engine & Compliance Chain** ([engine.py](file:///c:/Users/info/Documents/Sentinell/backend/app/compliance/engine.py)): Valutazione a doppia data (oggi vs `deploy_date`), Compliance Chain Traversal per risalire fino alla fonte normativa con `legal_weight` e spiegazioni RAG.
- **Report per Aree Cromatiche**: Report senza punteggio percentuale unico, con stati `COMPLIANT`, `NON_COMPLIANT`, `UNKNOWN` e `REQUIRES_HUMAN_REVIEW`.
- **API REST Compliance** ([router.py](file:///c:/Users/info/Documents/Sentinell/backend/app/api/router.py)): Endpoints per progetti, wizard, assessment, report, Compliance Chain e KB versions.
- **Suite di Test M4** ([test_m4_compliance_arks.py](file:///c:/Users/info/Documents/Sentinell/backend/tests/test_m4_compliance_arks.py)): 7 test di accettazione automatizzati per la Definition of Done della M4.

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
