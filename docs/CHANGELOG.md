# Changelog - AIGate

Tutti i cambiamenti notevoli a questo progetto saranno documentati in questo file.

## [Unreleased] - M1 Foundations (`m1-foundations`)

### Aggiunto
- Deposito delle specifiche di progetto in `docs/`:
  - `SPEC-ARCHITECTURE.md`: Invarianti I1-I3, modello a 3 zone, livelli architetturali e Gate.
  - `SPEC-DDL.sql`: DDL v0.1 con 17 tabelle relazionali e vincoli.
  - `SPEC-RULES-DSL.md`: DSL a tre valori per il Rule Engine.
  - `SPEC-PROVIDERS.md`: Matrice provider con vincoli di lock e egress.
- Struttura del repository backend in Python 3.12 e FastAPI.
- Modello delle Zone di Sicurezza (`backend/app/core/zones.py`) con decoratore `@requires_zone_max`.
- Gestore della Sessione e delle API Key su Keyring OS (`backend/app/core/security.py`).
- Client HTTP con Allowlist Egress (`backend/app/core/http_client.py`).
- Schema di database `data/aigate.db` e inizializzazione DDL (`backend/app/db/engine.py`).
- Vault cifrato SQLCipher / AES-GCM 256 con derivazione Argon2id (`backend/app/vault/manager.py`).
- Registro Audit Append-Only con Catena Crittografica Hash-Chain (`backend/app/audit/chain.py`).
- Valutatore DSL Three-Valued Logic (`backend/app/compliance/dsl.py`).
- Server FastAPI blindato su `127.0.0.1` (`backend/app/main.py`).
- Suite di test pytest completa per la Definition of Done della M1 (`backend/tests/test_m1_foundations.py`).
