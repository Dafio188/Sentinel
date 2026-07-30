from typing import Any, Dict, List, Optional
from backend.app.compliance.dsl import UNKNOWN, RuleDSLEvaluator
from backend.app.db.engine import get_db_connection

QUESTION_BANK: Dict[str, Dict[str, Any]] = {
    "Q_AI_DEF": {
        "id": "Q_AI_DEF",
        "text": "Il sistema utilizza tecniche di intelligenza artificiale (Machine Learning, LLM, Computer Vision, ecc.)?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["YES", "NO"],
        "var_name": "is_ai_system",
    },
    "Q_ROLE": {
        "id": "Q_ROLE",
        "text": "Qual è il vostro ruolo rispetto a questo sistema AI?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["PROVIDER", "DEPLOYER", "IMPORTER", "DISTRIBUTOR"],
        "var_name": "role",
    },
    "Q_DOMAIN": {
        "id": "Q_DOMAIN",
        "text": "In quale dominio operativo verrà impiegato il sistema?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["employment", "biometrics", "education", "critical_infrastructure", "general_public", "other"],
        "var_name": "domain",
    },
    "Q_PURPOSE": {
        "id": "Q_PURPOSE",
        "text": "Qual è la finalità specifica del sistema?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["evaluation", "recruitment", "promotion", "termination", "monitoring", "general_assistance"],
        "var_name": "purpose",
    },
    "Q_DATA_TYPES": {
        "id": "Q_DATA_TYPES",
        "text": "Quali categorie di dati vengono elaborate?",
        "answer_type": "MULTI_CHOICE",
        "options": ["IDENTIFIER", "SPECIAL", "FINANCIAL", "INDIRECT", "ANONYMOUS"],
        "var_name": "data_types",
    },
    "Q_AUTOMATION": {
        "id": "Q_AUTOMATION",
        "text": "Qual è il livello di automazione nel processo decisionale?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["SOLELY_AUTOMATED", "RECOMMENDATION", "HUMAN_IN_THE_LOOP"],
        "var_name": "automation_level",
    },
    "Q_SCALE": {
        "id": "Q_SCALE",
        "text": "Qual è la scala dell'elaborazione dati?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["SMALL", "MEDIUM", "LARGE"],
        "var_name": "scale",
    },
    "Q_OUTPUT_TYPE": {
        "id": "Q_OUTPUT_TYPE",
        "text": "Quale tipologia di output genera il sistema?",
        "answer_type": "SINGLE_CHOICE",
        "options": ["TEXT", "IMAGE", "VIDEO", "AUDIO"],
        "var_name": "output_type",
    },
    "Q_DEPLOY_DATE": {
        "id": "Q_DEPLOY_DATE",
        "text": "Qual è la data prevista per la messa in produzione (deployment)?",
        "answer_type": "DATE",
        "options": [],
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
