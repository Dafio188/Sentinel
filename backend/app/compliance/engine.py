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
            findings.append({
                "id": finding_id,
                "rule_id": rule_id,
                "framework": rule.get("framework"),
                "status": status,
                "applicable_today": applicable_today,
                "applicable_at_deploy": applicable_at_deploy,
                "effective_from": effective_from,
                "explanation": f"[spiegazione generata da AI] {explanation} (Fonte citata: {citation})",
                "source_refs": rule.get("source_refs", []),
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

            return {
                "finding_id": finding_id,
                "status": f["status"],
                "explanation": f["explanation"],
                "rule": rule_data,
                "source_refs": rule_data.get("source_refs", []),
                "chain_path": "Verdetto <- Azione <- Rischio <- Regola <- Articolo <- Fonte Normativa (EUR-Lex)",
            }
        finally:
            conn.close()
