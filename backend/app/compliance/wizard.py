from typing import Any, Dict, List, Optional
from backend.app.compliance.dsl import UNKNOWN, RuleDSLEvaluator
from backend.app.db.engine import get_db_connection

QUESTION_BANK: Dict[str, Dict[str, Any]] = {
    "Q_AI_DEF": {
        "id": "Q_AI_DEF",
        "text": "Il sistema utilizza tecniche di intelligenza artificiale (Machine Learning, LLM, Computer Vision, ecc.)?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["YES", "NO"],
        "options_detail": [
            {"value": "YES", "label": "SÌ / CONFERMATO", "desc": "Il sistema impiega modelli di apprendimento automatico, LLM o algoritmi di AI."},
            {"value": "NO", "label": "NO / NON PRESENTE", "desc": "Si tratta di software deterministico tradizionale senza componenti AI."}
        ],
        "var_name": "is_ai_system",
    },
    "Q_ROLE": {
        "id": "Q_ROLE",
        "text": "Qual è il vostro ruolo operativo rispetto a questo sistema AI?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["PROVIDER", "DEPLOYER", "IMPORTER", "DISTRIBUTOR"],
        "options_detail": [
            {"value": "PROVIDER", "label": "Fornitore / Provider", "desc": "Sviluppate o fate addestrare direttamente il modello o sistema AI."},
            {"value": "DEPLOYER", "label": "Utilizzatore / Deployer", "desc": "Utilizzate un sistema AI o un'API esterna per la vostra attività aziendale."},
            {"value": "IMPORTER", "label": "Importatore", "desc": "Importate un sistema AI sviluppato fuori dall'UE nel mercato europeo."},
            {"value": "DISTRIBUTOR", "label": "Distributore", "desc": "Commercializzate o distribuite un sistema AI sul mercato senza modificarlo."}
        ],
        "var_name": "role",
    },
    "Q_DOMAIN": {
        "id": "Q_DOMAIN",
        "text": "In quale settore o dominio operativo verrà impiegato il sistema?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["employment", "biometrics", "education", "critical_infrastructure", "general_public", "other"],
        "options_detail": [
            {"value": "employment", "label": "Risorse Umane e Lavoro", "desc": "Selezione del personale, valutazione lavoratori, promozioni o licenziamenti."},
            {"value": "biometrics", "label": "Biometria e Riconoscimento", "desc": "Identificazione biometrica, categorizzazione o analisi delle emozioni."},
            {"value": "education", "label": "Istruzione e Formazione", "desc": "Valutazione studenti, ammissione a corsi o esami automatizzati."},
            {"value": "critical_infrastructure", "label": "Infrastrutture Critiche", "desc": "Gestione reti elettriche, idriche, trasporti o sicurezza stradale."},
            {"value": "general_public", "label": "Servizi al Pubblico / Assistenza", "desc": "Chatbot di supporto clienti, assistenza informativa generale."},
            {"value": "other", "label": "Altro Settore Generico", "desc": "Elaborazione interna aziendale, produttività d'ufficio o uso generico."}
        ],
        "var_name": "domain",
    },
    "Q_PURPOSE": {
        "id": "Q_PURPOSE",
        "text": "Qual è la finalità specifica del sistema AI?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["evaluation", "recruitment", "promotion", "termination", "monitoring", "general_assistance"],
        "options_detail": [
            {"value": "evaluation", "label": "Valutazione delle Prestazioni", "desc": "Analisi delle performance, punteggi di produttività o merito."},
            {"value": "recruitment", "label": "Reclutamento e Selezione", "desc": "Filtro CV, colloqui automatizzati o posizionamento candidati."},
            {"value": "promotion", "label": "Avanzamento di Carriera", "desc": "Decisioni di promozione o assegnazione incarichi."},
            {"value": "termination", "label": "Cessazione o Licenziamento", "desc": "Valutazione per risoluzione contrattuale o licenziamento."},
            {"value": "monitoring", "label": "Monitoraggio Operativo", "desc": "Controllo delle attività dei lavoratori o comportamenti dei clienti."},
            {"value": "general_assistance", "label": "Assistenza e Produttività", "desc": "Generazione testi, ricerca informazioni o supporto operativo."}
        ],
        "var_name": "purpose",
    },
    "Q_DATA_TYPES": {
        "id": "Q_DATA_TYPES",
        "text": "Quali categorie di dati vengono elaborate dal sistema?",
        "answer_type": "MULTI_CHOICE",
        "options": ["IDENTIFIER", "SPECIAL", "FINANCIAL", "INDIRECT", "ANONYMOUS"],
        "options_detail": [
            {"value": "IDENTIFIER", "label": "Dati Identificativi Diretti", "desc": "Nome, Cognome, Codice Fiscale, Email, Numero di Telefono."},
            {"value": "SPECIAL", "label": "Dati Particolari / Sensibili (Art. 9)", "desc": "Dati sulla salute, opinioni politiche, orientamento, biometria."},
            {"value": "FINANCIAL", "label": "Dati Finanziari e Patrimoniali", "desc": "Fatturato, IBAN, dati bancari, carte di credito, retribuzione."},
            {"value": "INDIRECT", "label": "Dati Indirettamente Identificativi", "desc": "Indirizzo IP, dati catastali, numeri di registro/repertorio, ruolo."},
            {"value": "ANONYMOUS", "label": "Dati Anonimi o Aggregati", "desc": "Statistiche prive di alcun elemento riconducibile a persone fisiche."}
        ],
        "var_name": "data_types",
    },
    "Q_AUTOMATION": {
        "id": "Q_AUTOMATION",
        "text": "Qual è il livello di automazione nel processo decisionale?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["SOLELY_AUTOMATED", "RECOMMENDATION", "HUMAN_IN_THE_LOOP"],
        "options_detail": [
            {"value": "SOLELY_AUTOMATED", "label": "Totalmente Automatizzato", "desc": "Le decisioni vengono prese ed eseguite direttamente dall'AI senza intervento umano."},
            {"value": "RECOMMENDATION", "label": "Raccomandazione / Supporto", "desc": "L'AI fornisce un suggerimento o report, ma la decisione finale spetta a un umano."},
            {"value": "HUMAN_IN_THE_LOOP", "label": "Supervisione Umana Obbligatoria", "desc": "Un operatore umano valida ed approva ogni singolo passaggio prima dell'output."}
        ],
        "var_name": "automation_level",
    },
    "Q_SCALE": {
        "id": "Q_SCALE",
        "text": "Qual è la scala dell'elaborazione dati?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["SMALL", "MEDIUM", "LARGE"],
        "options_detail": [
            {"value": "SMALL", "label": "Piccola Scala", "desc": "Uso interno ristretto o meno di 1.000 soggetti interessati."},
            {"value": "MEDIUM", "label": "Media Scala", "desc": "Utilizzo aziendale diffuso (tra 1.000 e 50.000 soggetti interessati)."},
            {"value": "LARGE", "label": "Larga Scala", "desc": "Elaborazione massiva, oltre 50.000 soggetti interessati o copertura nazionale."}
        ],
        "var_name": "scale",
    },
    "Q_OUTPUT_TYPE": {
        "id": "Q_OUTPUT_TYPE",
        "text": "Quale tipologia di contenuto genera il sistema?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["TEXT", "IMAGE", "VIDEO", "AUDIO"],
        "options_detail": [
            {"value": "TEXT", "label": "Testo / Documenti", "desc": "Generazione o analisi di testi, report, contratti o risposte."},
            {"value": "IMAGE", "label": "Immagini / Grafica", "desc": "Generazione o elaborazione di immagini e contenuti visivi."},
            {"value": "VIDEO", "label": "Video / Animazioni", "desc": "Generazione o analisi di filmati video."},
            {"value": "AUDIO", "label": "Audio / Voce", "desc": "Sintesi vocale, trascrizione o elaborazione audio."}
        ],
        "var_name": "output_type",
    },
    "Q_DEPLOY_DATE": {
        "id": "Q_DEPLOY_DATE",
        "text": "Qual è la data prevista per la messa in produzione (deployment)?",
        "answer_type": "DATE",
        "options": [],
        "options_detail": [],
        "var_name": "deploy_date",
    },
}

SEVERITY_WEIGHT = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MED": 2,
    "MEDIUM": 2,
    "LOW": 1,
}

class AdaptiveWizard:
    def get_next_question(self, project_model: Dict[str, Any], rules: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        # 1. Q_AI_DEF is always first if not answered
        if "is_ai_system" not in project_model:
            return QUESTION_BANK["Q_AI_DEF"]

        if project_model.get("is_ai_system") == "NO":
            # If not AI system, filter out AI Act rules
            rules = [r for r in rules if r.get("framework") != "AI_ACT"]

        # Evaluate rules and collect missing information asked in on_unknown.ask
        ask_weights: Dict[str, int] = {}
        for r in rules:
            cond_res = RuleDSLEvaluator.evaluate(r.get("condition", {}), project_model)
            if RuleDSLEvaluator.is_unknown(cond_res):
                on_unk = r.get("on_unknown", {})
                asked = on_unk.get("ask", [])
                weight = SEVERITY_WEIGHT.get(r.get("severity", "LOW"), 1)
                for q_id in asked:
                    var_name = QUESTION_BANK.get(q_id, {}).get("var_name")
                    if var_name and var_name not in project_model:
                        ask_weights[q_id] = ask_weights.get(q_id, 0) + weight

        if not ask_weights:
            # Check remaining unanswered questions in bank
            for q_id, q_data in QUESTION_BANK.items():
                if q_data["var_name"] not in project_model:
                    return q_data
            return None

        # Sort candidate questions by weight descending, then alphabetically by q_id
        sorted_candidates = sorted(ask_weights.keys(), key=lambda q: (-ask_weights[q], q))
        next_q_id = sorted_candidates[0]
        return QUESTION_BANK.get(next_q_id)
