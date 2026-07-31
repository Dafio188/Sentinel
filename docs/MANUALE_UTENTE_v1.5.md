# Sentinell — Local AI Privacy & Compliance Gateway
## Manuale di Utilizzo — Versione 1.5 (Aggiornato)

Documento ufficiale di guida operativa della piattaforma **Sentinell**.

---

## 📐 Indice
1. [Cos'è Sentinell](#1-cosè-sentinell)
2. [Prima di Iniziare](#2-prima-di-iniziare)
   - 2.1 [Cosa Serve](#21-cosa-serve)
   - 2.2 [Primo Avvio & Configurazione Vault](#22-primo-avvio--configurazione-vault)
3. [La Schermata Principale (Dashboard & Scenari)](#3-la-schermata-principale-dashboard--scenari)
4. [Area Privacy — Protezione Documenti & Modello Rizzo-PII](#4-area-privacy--protezione-documenti--modello-rizzo-pii)
   - 4.1 [Caricare un Documento](#41-caricare-un-documento)
   - 4.2 [Motore di Analisi Rizzo-PII & Entità Italiane](#42-motore-di-analisi-rizzo-pii--entità-italiane)
   - 4.3 [Le Quattro Modalità di Protezione](#43-le-quattro-modalità-di-protezione)
   - 4.4 [Livelli di Policy & Controllo Finale](#44-livelli-di-policy--controllo-finale)
   - 4.5 [Download Sicuro del File Protetto](#45-download-sicuro-del-file-protetto)
5. [Area Compliance — Valutazione Progetti (EU AI Act & GDPR)](#5-area-compliance--valutazione-progetti-eu-ai-act--gdpr)
   - 5.1 [AI Auto-Extraction & Ingestion Automatico](#51-ai-auto-extraction--ingestion-automatico)
   - 5.2 [Il Wizard Guidato in Italiano & Selettore Data Deployment](#52-il-wizard-guidato-in-italiano--selettore-data-deployment)
   - 5.3 [Report Cromatico & Azioni Correttive Specifiche](#53-report-cromatico--azioni-correttive-specifiche)
   - 5.4 [Compliance Chain Traversal (Tracciabilità Legale EUR-Lex)](#54-compliance-chain-traversal-tracciabilità-legale-eur-lex)
   - 5.5 [Download dell'Audit Report Formale](#55-download-dellaudit-report-formale)
6. [Area AI Workspace — Conversare in Sicurezza](#6-area-ai-workspace--conversare-in-sicurezza)
   - 6.1 [Classificazione dei Provider](#61-classificazione-dei-provider)
   - 6.2 [Gestione del Provvedimento DeepSeek & Servizi Bloccati](#62-gestione-del-provvedimento-deepseek--servizi-bloccati)
7. [Area Test di Attacco (Adversarial Testing)](#7-area-test-di-attacco-adversarial-testing)
8. [Domande Frequenti (FAQ)](#8-domande-frequenti-faq)
9. [Glossario Essenziale](#9-glossario-essenziale)

---

## 1. Cos'è Sentinell

**Sentinell** è un'applicazione desktop/server locale sviluppata per garantire il controllo totale della privacy e della conformità normativa quando si utilizza l'intelligenza artificiale in azienda, in strutture sanitarie o negli studi professionali.

Sentinell svolge due funzioni fondamentali:

1. **Protezione Dati & Privacy Engine (Rizzo-PII)**: Prima che un documento o un prompt venga inviato ad un'AI cloud (ChatGPT, Claude, Gemini, DeepSeek o altri), Sentinell analizza il testo con il motore locale **Rizzo-PII (0.3B)** ed elimina/maschera/pseudonimizza automaticamente Nomi, Codici Fiscali, Partite IVA, Dati Sanitari, IBAN e Documenti senza che nulla esca dal computer non autorizzato.
2. **Compliance Engine & ARKS (GDPR + EU AI Act)**: Prima di lanciare o utilizzare un progetto basato su AI (es. screening di CV, analisi di cartelle cliniche o valutazioni automatizzate), Sentinell calcola la conformità deterministica al GDPR ed all'EU AI Act dell'Unione Europea, fornendo **azioni correttive operative e specifiche**.

> 💡 **Principio Guida Fondamentale**: Sentinell non allucina e non sostituisce il giudizio umano. Calcola ed applica regole deterministiche, indica gli articoli di legge EUR-Lex applicabili e specifica dove è richiesta una revisione o sorveglianza umana obbligatoria (*Human-in-the-loop*).

---

## 2. Prima di Iniziare

### 2.1 Cosa Serve
* **Un computer locale** con supporto a Python 3.11/3.12 e Node.js.
* **Ollama (Opzionale)**: Se desideri chattare in locale con modelli open-source senza alcuna connessione internet.
* **Chiavi API Esterne (Opzionale)**: Se intendi utilizzare Google Gemini, OpenAI o Anthropic, le cui chiavi API vengono salvate in modo sicuro nel credential store del sistema operativo (Keyring/Vault), mai in chiaro nei file dell'applicazione.

### 2.2 Primo Avvio & Configurazione Vault
* Al primo avvio viene generata la master key per il **Vault Cifrato AES-GCM 256**, il contenitore sicuro isolato dove vengono conservate le corrispondenze tra i dati reali ed i codici di pseudonimizzazione (`PERSONA_001`).
* **Nota di Sicurezza**: I dati originali ed il Vault vivono in **Zona 0 (Riservata)** e non possono mai essere trasmessi a server esterni.

---

## 3. La Schermata Principale (Dashboard & Scenari)

All'apertura di Sentinell trovi la barra di stato in tempo reale ed i **3 Scenari Operativi Rapidi**:

| Scenario | A cosa serve | Esempio Pratico |
| :--- | :--- | :--- |
| 🩺 **Sanità & Medici** | Anonimizzazione cartelle cliniche in locale con Rizzo-PII prima dell'invio ad un'AI ed analisi rischi dati sanitari ex Art. 9 GDPR. | Cartella clinica di un paziente con diagnosi da analizzare con un LLM. |
| 👥 **HR & Selezione CV** | Valutazione della conformità dei sistemi di screening candidati e filtri assunzioni ai sensi dell'Allegato III dell'EU AI Act. | Uso di Gemini per vagliare e classificare i CV ricevuti in azienda. |
| 💻 **Dev & API Cloud** | Scansione automatica di prompt/payload e verifica trasferimenti dati Extra-UE (Capo V GDPR). | Integrazione di API cloud per assistenza clienti o sintesi documenti. |

---

## 4. Area Privacy — Protezione Documenti & Modello Rizzo-PII

### 4.1 Caricare un Documento
Puoi caricare file PDF, Word, Excel, testo semplice o immagini/scansioni (grazie all'OCR integrato). Il documento originale resta memorizzato in **Zona 0** inaccessibile dall'esterno.

### 4.2 Motore di Analisi Rizzo-PII & Entità Italiane
Sentinell impiega il modello locale avanzato **Rizzo-PII (0.3B / ModernBERT)** integrato con il **Pattern Gate Italiano**, in grado di riconoscere ed estrarre:

| Categoria | Tipo di Dato Rilevato | Esempi |
| :--- | :--- | :--- |
| 🔴 **Dati Particolari / Sensibili** | Salute, patologie, diagnosi, biometria, convinzioni religiose/politiche (Art. 9 GDPR) | Diagnosi medica, gruppo sanguigno |
| 🟠 **Identificativi Diretti** | Codice Fiscale, Partita IVA, Documenti (DOCID), Nome, Cognome, Email, IBAN, Telefono | `RSSMRA80A01H501U`, `IT12345678901` |
| 🟡 **Identificativi Indiretti** | Dati Catastali (CATASTO), Province, Ruoli aziendali e combinazioni uniche | "Dirigente dell'ufficio tecnico del Comune X" |
| 🔵 **Dati Finanziari** | Stipendi, retribuzioni, importi di conti | "Retribuzione annua lorda € 45.000" |

### 4.3 Le Quattro Modalità di Protezione
* **Maschera**: Sostituisce il dato con un'etichetta generica non reversibile (`Mario Rossi` ➔ `[PERSONA]`).
* **Pseudonimizza**: Sostituisce il dato con un codice reversibile tramite Vault (`Mario Rossi` ➔ `PERSONA_001`).
* **Generalizza**: Rende il dato generico (`53 anni` ➔ `50-60 anni`).
* **Anonimizza (Semantica)**: Riscrive la frase mantenendo il senso clinico/operativo ma eliminando ogni dettaglio identificativo.

### 4.4 Livelli di Policy & Controllo Finale
Prima dell'invio, il **Zero-Residue Validator** calcola il punteggio di rischio: se rileva PII residue non protette, blocca l'invio ed avvisa l'operatore.

### 4.5 Download Sicuro del File Protetto
Cliccando su **"Scarica File Protetto"**, Sentinell genera ed invia in modo autenticato (tramite session token) il documento bonificato pronto per il download sicuro.

---

## 5. Area Compliance — Valutazione Progetti (EU AI Act & GDPR)

### 5.1 AI Auto-Extraction & Ingestion Automatico
Quando crei un nuovo progetto inserendo Nome e Finalità (es. *"Utilizzando Gemini devo analizzare dei CV di candidati"*), Sentinell attiva il **ProjectFeatureExtractor**:
* Analizza il testo ed estrae automaticamente: **Sistema AI (SÌ)**, **Ruolo (Deployer)**, **Dominio (Risorse Umane / Employment)**, **Finalità (Reclutamento)**, **Dati (Identificativi + Sensibili)**.
* Pre-compila le schede del progetto e **salta le domande ridondanti del wizard**.

### 5.2 Il Wizard Guidato in Italiano & Selettore Data Deployment
* Le domande sono presentate con **schede descrittive ed etichette esplicative in italiano chiaro**.
* Per le domande temporali (es. `Q_DEPLOY_DATE`), Sentinell mette a disposizione un **selettore di data formale** ed il pulsante rapido **"Oggi (Già in Produzione)"**.

### 5.3 Report Cromatico & Azioni Correttive Specifiche
Sentinell non restituisce un vago punteggio, ma un esito prescrittivo chiaro:

| Stato | Significato | Azione Correttiva Generata (Esempio per HR / CV) |
| :--- | :--- | :--- |
| 🟢 **Conforme** | Requisito soddisfatto | Nessuna azione correttiva necessaria. |
| 🟡 **Revisione Richiesta** | Sistema ad Alto Rischio (Allegato III) | **"Eseguire Valutazione di Impatto sui Diritti Fondamentali (FRIA ex Art. 49 AI Act), registrare il sistema nella Banca Dati UE e stabilire la sorveglianza umana (Human-in-the-loop) per i CV."** |
| 🔴 **Non Conforme / Vietato** | Violazione o Pratica Proibita (Art. 5) | **"Blocco operatività: Interruzione immediata prima del deployment."** |

### 5.4 Compliance Chain Traversal (Tracciabilità Legale EUR-Lex)
Cliccando su ciascuna violazione, l'albero di tracciabilità ricostruisce la catena dal verdetto fino alla norma originaria EUR-Lex (es. `EU_2024_1689 Art. 6` o `EU_2016_679 Art. 35`).

### 5.5 Download dell'Audit Report Formale
Cliccando sul pulsante **`Scarica Audit Report`** 📥 in alto a destra nel report, scarichi il file **`sentinell_compliance_report_[id_progetto].json`** contenente la certificazione formale dell'audit da allegare alla documentazione per il DPO o per l'Autorità Garante.

---

## 6. Area AI Workspace — Conversare in Sicurezza

### 6.1 Classificazione dei Provider
* 🟢 **Locale (Ollama)**: Esecuzione interamente sul computer dell'utente (100% offline).
* 🟢 **Fidato (Enterprise Cloud)**: Servizi cloud con garanzie contrattuali ed isolamento dati.
* 🟡 **Esterno (OpenAI / Gemini Paid)**: Soggetto a controlli Pre-flight/Post-flight del Privacy Gate.
* 🔴 **Bloccato**: Servizi con limitazioni o provvedimenti delle Autorità.

### 6.2 Gestione del Provvedimento DeepSeek & Servizi Bloccati
In ottemperanza ai provvedimenti delle Autorità di Protezione Dati (Garante Privacy), Sentinell impedisce l'invio di dati pseudonimizzati verso servizi bloccati come DeepSeek, ammettendo esclusivamente testi al 100% anonimizzati.

---

## 7. Area Test di Attacco (Adversarial Testing)

Consente di verificare la robustezza del sistema eseguendo test avversariali locali (es. Codici Fiscali spezzati, omissione di spazi, prompt injection nei documenti) per valutare l'affidabilità del Privacy Engine prima dell'impiego operativo.

---

## 8. Domande Frequenti (FAQ)

1. **I miei documenti originali escono mai dal computer?**  
   *No.* I documenti di Zona 0 restano memorizzati sul tuo disco e non possono mai essere trasmessi all'esterno.
2. **Serve una API key a pagamento per fare valutazioni di compliance?**  
   *No.* Sentinell include il motore semantico deterministico `ProjectFeatureExtractor` ed il motore ARKS che funzionano interamente in locale senza richiedere API key.
3. **Sentinell garantisce che sono automaticamente a norma senza legge?**  
   *No.* Sentinell fornisce un audit deterministico e prescrive le azioni da compiere, ma la validazione formale e la sorveglianza decisionale spettano sempre alla valutazione umana (*Human-in-the-loop*).
4. **Posso scaricare un certificato formale dell'audit?**  
   *Sì.* Nel report di conformità è disponibile il pulsante `Scarica Audit Report` per esportare la certificazione formale dell'audit in formato JSON.

---

## 9. Glossario Essenziale

* **Rizzo-PII**: Modello avanzato di riconoscimento entità personali (NER) per la lingua italiana ed identificativi legali.
* **ARDS / ARKS**: Sistema di Retrieval & Knowledge Base normativa contenente il testo e le regole del GDPR ed EU AI Act.
* **FRIA**: *Fundamental Rights Impact Assessment* (Valutazione d'Impatto sui Diritti Fondamentali ex Art. 49 EU AI Act per sistemi ad alto riskio).
* **DPIA**: *Data Protection Impact Assessment* (Valutazione d'Impatto sulla Protezione dei Dati ex Art. 35 GDPR).
* **Human-in-the-loop**: Requisito di sorveglianza umana obbligatoria che impedisce ad un'AI di prendere decisioni autonome senza la convalida di un operatore umano.
