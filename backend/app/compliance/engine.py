import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.arks.retrieval import ArksRetrieval
from backend.app.compliance.dsl import UNKNOWN, RuleDSLEvaluator
from backend.app.db.engine import get_db_connection

class ComplianceEngine:
    def __init__(self, kb_version: str = "KB-2026.07-B"):
        self.kb_version = kb_version
        self.retrieval = ArksRetrieval()

    def load_rules(self) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        rules_dir = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "rules"
        if rules_dir.exists():
            for f in rules_dir.glob("*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as file:
                        rules.append(json.load(file))
                except Exception:
                    pass

        # Sync rules into 'rules' database table to satisfy Foreign Key constraints
        if rules:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                for r in rules:
                    on_t = r.get("on_true", {})
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO rules (
                            id, framework, category, severity, title, condition_json,
                            action, human_review, source_refs_json, kb_version
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            r["rule_id"],
                            r.get("framework", "GDPR"),
                            r.get("category", "GENERAL"),
                            r.get("severity", "MEDIUM"),
                            r.get("title", "Regola Compliance"),
                            json.dumps(r.get("condition", {})),
                            on_t.get("action", "REVIEW"),
                            1 if on_t.get("human_review") else 0,
                            json.dumps(r.get("source_refs", [])),
                            r.get("kb_version", self.kb_version),
                        ),
                    )
                conn.commit()
            finally:
                conn.close()

        return rules

    def assess_project(
        self,
        project_id: str,
        project_model: Dict[str, Any],
        deploy_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        rules = self.load_rules()
        findings: List[Dict[str, Any]] = []

        eval_today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        eval_deploy = deploy_date or project_model.get("deploy_date") or eval_today

        has_non_compliant = False
        has_unknown = False
        has_review = False

        for rule in rules:
            rule_id = rule["rule_id"]
            effective_from = rule.get("effective_from")

            applicable_today = (effective_from is None or effective_from <= eval_today)
            applicable_at_deploy = (effective_from is None or effective_from <= eval_deploy)

            res = RuleDSLEvaluator.evaluate(rule.get("condition", {}), project_model)

            status = "MET"
            explanation = ""

            if RuleDSLEvaluator.is_unknown(res):
                status = "UNKNOWN"
                has_unknown = True
                asked_vars = rule.get("on_unknown", {}).get("ask", [])
                explanation = f"Informazioni insufficienti. Rispondere alle domande: {asked_vars}"
            elif res is True or (isinstance(res, (int, float)) and res > 0):
                on_true = rule.get("on_true", {})
                action = on_true.get("action", "REVIEW")
                if action == "BLOCK":
                    status = "NOT_MET"
                    has_non_compliant = True
                else:
                    status = "REVIEW"
                    has_review = True

                if not applicable_today and applicable_at_deploy:
                    explanation = f"Obbligo non ancora applicabile oggi — lo sarà alla data di deployment ({effective_from})"
                else:
                    explanation = f"Regola attivata: {on_true.get('finding', 'Rilevamento')}"
            else:
                status = "MET"
                explanation = "Requisito di conformità rispettato."

            chunks = self.retrieval.search(f"{rule.get('framework')} {rule.get('title')}", self.kb_version, eval_today, top_k=1)
            citation = chunks[0]["id"] if chunks else "EUR_LEX_CIT"

            finding_id = f"fnd_{uuid.uuid4().hex[:12]}"
            title = rule.get("title", rule_id)
            severity = rule.get("severity", "MEDIUM")
            sources = rule.get("source_refs", [])
            source_article = ", ".join([f"{s.get('source_id', '')} Art. {s.get('article', '')}" for s in sources]) if sources else "Regolamento UE"

            action_req = get_specific_action_required(rule_id, status)

            color = "RED" if status == "NOT_MET" else "AMBER" if status in ("REVIEW", "REQUIRES_HUMAN_REVIEW") else "WHITE" if status == "UNKNOWN" else "GREEN"

            findings.append({
                "id": finding_id,
                "rule_id": rule_id,
                "title": title,
                "severity": severity,
                "color_code": color,
                "action_required": action_req,
                "framework": rule.get("framework"),
                "status": status,
                "applicable_today": applicable_today,
                "applicable_at_deploy": applicable_at_deploy,
                "effective_from": effective_from,
                "source_article": source_article,
                "explanation": f"[spiegazione generata da AI] {explanation} (Fonte citata: {citation})",
                "source_refs": sources,
            })

        if has_non_compliant:
            overall_status = "NON_COMPLIANT"
        elif has_review:
            overall_status = "REQUIRES_HUMAN_REVIEW"
        elif has_unknown:
            overall_status = "UNKNOWN"
        else:
            overall_status = "COMPLIANT"

        assessment_id = f"ass_{uuid.uuid4().hex[:12]}"
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO assessments (
                    id, project_id, kb_version, gdpr_status, aiact_class, summary_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_id,
                    project_id,
                    self.kb_version,
                    overall_status,
                    overall_status,
                    json.dumps({"total_rules": len(rules), "overall_status": overall_status}),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            for f in findings:
                cursor.execute(
                    """
                    INSERT INTO assessment_findings (
                        id, assessment_id, rule_id, status, confidence, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (f["id"], assessment_id, f["rule_id"], f["status"], 0.95, f["explanation"]),
                )
            conn.commit()
        finally:
            conn.close()

        return {
            "assessment_id": assessment_id,
            "project_id": project_id,
            "overall_status": overall_status,
            "findings_count": len(findings),
            "findings": findings,
        }

    def get_compliance_chain(self, finding_id: str) -> Dict[str, Any]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assessment_findings WHERE id = ?", (finding_id,))
            f = cursor.fetchone()
            if not f:
                return {}
            
            rule_id = f["rule_id"]
            rules = self.load_rules()
            target_rule = [r for r in rules if r["rule_id"] == rule_id]
            rule_data = target_rule[0] if target_rule else {}

            sources = rule_data.get("source_refs", [])
            source_desc = ", ".join([f"{s.get('source_id', '')} Art. {s.get('article', '')}" for s in sources]) if sources else "Normativa EUR-Lex"

            status = f["status"]
            action = get_specific_action_required(rule_id, status)

            return {
                "finding_id": finding_id,
                "verdict": status,
                "action": action,
                "rule_id": rule_id,
                "rule_title": rule_data.get("title", rule_id),
                "severity": rule_data.get("severity", "MEDIUM"),
                "source_article": source_desc,
                "explanation": f["explanation"],
                "rule": rule_data,
                "source_refs": sources,
                "chain_path": f"Esito Finale: {status} ➔ Azione: {action} ➔ Regola: {rule_data.get('title', rule_id)} ➔ Riferimento Normativo: {source_desc}",
            }
        finally:
            conn.close()


def get_specific_action_required(rule_id: str, status: str) -> str:
    """
    Restituisce un'azione correttiva specifica, operativa e prescrittiva
    basata sulla norma violata o soggetta a revisione.
    """
    actions_map = {
        "AIACT.ANNEX3.EMPLOYMENT": {
            "NOT_MET": "Blocco operatività: L'uso di un sistema AI per selezione/valutazione del personale (HR) senza le garanzie dell'Allegato III costituisce una violazione dell'Art. 6 EU AI Act.",
            "REVIEW": "Eseguire Valutazione di Impatto sui Diritti Fondamentali (FRIA), registrare il sistema nella Banca Dati UE dei sistemi ad alto rischio (Art. 49) e stabilire una procedura formale di sorveglianza umana (Human-in-the-loop) per validare o revocare le decisioni prese dall'AI sui CV.",
            "UNKNOWN": "Completare nel wizard l'indicazione del settore e delle finalità d'uso per verificare l'assoggettamento alla disciplina degli altoparlanti e sistemi HR ad alto rischio.",
            "MET": "Sistema HR conforme ai requisiti dell'Allegato III e presidiato da sorveglianza umana."
        },
        "GDPR.ART35.DPIA": {
            "NOT_MET": "Blocco trattamenti: L'analisi di CV contenenti dati identificativi o sensibili con profilazione/automazione richiede obbligatoriamente una DPIA ex Art. 35 GDPR prima dell'avvio.",
            "REVIEW": "Redigere la DPIA (Valutazione d'Impatto sulla Protezione dei Dati) ai sensi dell'Art. 35 GDPR, documentando la minimizzazione dei dati, i rischi di discriminazione/bias sui candidati e consultando il DPO prima del deployment.",
            "UNKNOWN": "Completare la selezione dei tipi di dati trattati e del livello di automazione nel wizard per determinare l'obbligo di DPIA.",
            "MET": "DPIA completata con esito favorevole e misure di mitigazione del rischio attive."
        },
        "GDPR.CH5.TRANSFER": {
            "NOT_MET": "Blocco trasferimento: Il trasferimento dei dati dei candidati verso server Extra-UE (es. USA) senza basi giuridiche o decisioni di adeguatezza viola il Capo V del GDPR.",
            "REVIEW": "Verificare ed allegare le Clausole Contrattuali Standard (SCC) o verificare l'adesione del provider (es. Google / OpenAI) al EU-US Data Privacy Framework (DPF) per l'invio dei dati personali ai server cloud.",
            "UNKNOWN": "Indicare l'ubicazione dei server del provider AI utilizzato.",
            "MET": "Trasferimento Extra-UE garantito da decisioni di adeguatezza o Clausole Contrattuali Standard (SCC)."
        },
        "AIACT.ART5.NCII": {
            "NOT_MET": "PRATICA VIETATA (Art. 5 EU AI Act): Blocco ed eliminazione immediata del sistema. È vietata la generazione o diffusione di contenuti intimi non consenzienti.",
            "REVIEW": "Fermare lo sviluppo ed attivare audit di sicurezza sulla condotta del modello.",
            "UNKNOWN": "Confermare la tipologia di output generato ed il consenso degli interessati.",
            "MET": "Sistema conforme ai divieti dell'Art. 5 EU AI Act."
        }
    }
    
    rule_actions = actions_map.get(rule_id, {})
    if status in rule_actions:
        return rule_actions[status]
    
    if status == "NOT_MET":
        return "Intervento urgente richiesto: blocco o adeguamento prima del deployment per violazione della norma."
    elif status == "REVIEW":
        return "Revisione d'impatto e validazione formale raccomandata prima della messa in produzione."
    elif status == "UNKNOWN":
        return "Completare le risposte pendenti nel wizard per verificare il rispetto della norma."
    else:
        return "Nessuna azione correttiva necessaria (Requisito Conforme)."
