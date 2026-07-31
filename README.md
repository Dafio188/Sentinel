# 🛡️ Sentinel — Local AI Privacy & Compliance Gateway

**Sentinel** è la piattaforma Zero-Trust & Local-First per l'anonimizzazione dei dati, la conformità normativa (EU AI Act & GDPR) e il controllo dei gateway LLM in ambienti aziendali riservati.

---

## 🚀 Avvio Rapido con Docker (Raccomandato)

Requisiti: [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato.

Per avviare l'intera piattaforma (Backend FastAPI + Frontend Next.js):

```bash
docker compose up -d
```

- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000/health](http://localhost:8000/health)

Per fermare i container:
```bash
docker compose down
```

---

## 🛠️ Avvio Manuale per Sviluppatori

### 1. Backend (FastAPI / Python 3.12+)
```bash
# Installa dipendenze
pip install -e .

# Avvia il server backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend (Next.js 14 / Node 20+)
```bash
cd frontend
npm install
npm run dev
```

---

## 🏛️ Architettura & Funzionalità

1. **Privacy Center**: Rilevamento e mascheramento dinamico di PII, codici fiscali, carte di credito, email e dati sanitari/finanziari con supporto per il motore **RIZZO**.
2. **Compliance Wizard**: Valutazione dei sistemi AI secondo la classificazione dei rischi dell'**EU AI Act** (Art. 6 & Allegato III).
3. **LLM Gateway**: Proxy intelligente con Preflight Gate per prevenire l'invio di dati riservati a provider esterni o LLM locali (Ollama).
4. **Audit & ARKS**: Registro immutabile delle scansioni e catena di evidenze trasparenti.

---

## 📄 Licenza
Proprietà riservata — Sentinel Platform 2026.
