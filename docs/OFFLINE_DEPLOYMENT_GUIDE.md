# AIGate — Guida all'Installazione ed all'Uso Offline (Air-Gapped)

Questa guida illustra la procedura di installazione ed esecuzione in locale di **AIGate — Local AI Privacy & Compliance Gateway** in ambienti completamente isolati dalla rete (air-gapped).

---

## 🔒 Prerequisiti
1. **Python 3.11 / 3.12** installato nel sistema locale.
2. **Node.js 18+** per l'interfaccia frontend Next.js.
3. **Ollama Locale** (opzionale, per inferenza ed embedding completamente offline con modelli `gemma4` e `nomic-embed-text`).

---

## 🚀 Avvio Rapido

### Su Windows:
Doppio click sul file `start_aigate.bat` oppure da terminale:
```cmd
.\start_aigate.bat
```

### Su Linux / macOS:
Rendere lo script eseguibile ed avviarlo:
```bash
chmod +x start_aigate.sh
./start_aigate.sh
```

---

## 🌐 Indirizzi dei Servizi Locali
- **Dashboard Desktop UI**: `http://localhost:3000`
- **Backend API Gateway**: `http://127.0.0.1:8000/api`
- **Documentazione OpenAPI Swagger**: `http://127.0.0.1:8000/docs`

---

## 🔑 Gestione del Vault Cifrato
All'avvio, il Vault crittografico `data/vault.db` utilizza derivazione Argon2id / PBKDF2 e cifratura AES-GCM 256 per memorizzare le tabelle di pseudonimizzazione (`REPLACE`).
La passphrase del Vault può essere fornita via UI durante le operazioni di protezione nel Privacy Center.

---

## 📜 Ingestione di Nuove Fonti Normative (ARKS)
Per aggiornare la Knowledge Base ARKS in locale:
1. Scaricare i file normativi ufficiali (EUR-Lex / EDPB) seguendo le indicazioni in [scripts/fetch_sources.md](file:///c:/Users/info/Documents/Sentinell/scripts/fetch_sources.md).
2. Salvare i file nelle rispettive cartelle sotto `knowledge/sources/`.
3. Eseguire l'ingestione tramite gli strumenti ARKS integrati o riavviare il gateway per l'indicizzazione automatica.
