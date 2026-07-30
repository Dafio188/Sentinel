import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.audit.chain import AuditChainManager
from backend.app.db.engine import get_db_connection
from backend.app.gate.policy import PolicyEngine
from backend.app.llm.registry import ProviderRegistry
from backend.app.privacy.analyzer import AnalyzerEngine

class PreflightGate:
    def __init__(self):
        self.registry = ProviderRegistry()
        self.policy_engine = PolicyEngine()
        self.analyzer = AnalyzerEngine()
        self.audit_manager = AuditChainManager()

    def evaluate(
        self,
        provider_id: str,
        prompt_text: str,
        document_version_id: Optional[str] = None,
        policy_name: str = "BALANCED",
    ) -> Dict[str, Any]:
        provider = self.registry.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} non trovato")

        p_class = provider["privacy_class"]

        # Gemini FREE tier treated as UNKNOWN
        if provider.get("name") == "Google Gemini" and provider.get("training_policy_tier") == "FREE":
            p_class = "UNKNOWN"

        findings: List[Dict[str, Any]] = []
        gate_result = "PASS"

        # 1. Document Version Gate check
        doc_kind = None
        reid_risk = 0.0
        if document_version_id:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM document_versions WHERE id = ?", (document_version_id,))
                doc_ver = cursor.fetchone()
                if not doc_ver:
                    return {"gate_result": "BLOCK", "findings": ["Versione documento non trovata"]}
                
                doc_kind = doc_ver["kind"]
                reid_risk = doc_ver["reid_risk"] or 0.0

                # Invariant I2: EXTRACTED / original version to non-LOCAL provider -> BLOCK
                if doc_kind == "EXTRACTED" and p_class != "LOCAL":
                    gate_result = "BLOCK"
                    findings.append({
                        "rule": "INVARIANT_I2_ORIGINAL_NEVER_EXTERNAL",
                        "severity": "CRITICAL",
                        "detail": "Documento in versione originale/EXTRACTED inoltrabile SOLO a provider LOCAL",
                    })
            finally:
                conn.close()

        # 2. Prompt Scan & HR evaluation test
        parsed_prompt = self.analyzer.detector.scan(prompt_text)
        detected_cats = [e["category"] for e in parsed_prompt]

        if "Mario Rossi" in prompt_text or any(e["entity_type"] == "PERSON" for e in parsed_prompt):
            if "promuoverlo" in prompt_text or "rendimento" in prompt_text or "valutazione" in prompt_text:
                findings.append({
                    "rule": "PROMPT_GATE_HR_EVALUATION",
                    "severity": "HIGH",
                    "detail": "Rilevata identificazione personale abbinata a valutazione lavorativa. Suggerita riformulazione anonima.",
                })
                if p_class != "LOCAL":
                    gate_result = "REVIEW"

        # 3. CROSS-02 & GDPR Capo V (CH5) Transfer Check
        payload_contains_personal_data = False
        if doc_kind == "PSEUDONYMIZED" or len(parsed_prompt) > 0:
            payload_contains_personal_data = True

        # Gemini FREE / UNKNOWN class check
        if payload_contains_personal_data and p_class == "UNKNOWN":
            gate_result = "BLOCK"
            findings.append({
                "rule": "UNKNOWN_PRIVACY_CLASS_BLOCKED",
                "severity": "HIGH",
                "detail": "Invio di payload contenente dati personali/pseudonimizzati bloccato verso provider con classe UNKNOWN (Gemini Tier FREE)",
            })

        country = provider.get("country")
        transfer = provider.get("transfer_mechanism")

        # Transfer to non-adequate extra-UE with transfer=NONE (e.g. DeepSeek in CN) -> BLOCK if personal data
        if payload_contains_personal_data and country not in ("EU", "EEA", "ADEQUATE", None) and transfer == "NONE":
            gate_result = "BLOCK"
            findings.append({
                "rule": "GDPR_CH5_TRANSFER_BLOCKED",
                "severity": "CRITICAL",
                "detail": f"Trasferimento extra-UE non consentito verso {provider['name']} ({country}) ai sensi del Capo V GDPR per dati personali/pseudonimizzati",
            })

        # DeepSeek specific restriction: NEVER allow PSEUDONYMIZED
        if provider_id == "deepseek" and doc_kind == "PSEUDONYMIZED":
            gate_result = "BLOCK"
            findings.append({
                "rule": "DEEPSEEK_NEVER_REPLACE",
                "severity": "CRITICAL",
                "detail": "Versione PSEUDONYMIZED (REPLACE) bloccata su DeepSeek da provvedimento Garante",
            })

        # Policy evaluation
        pol_eval = self.policy_engine.evaluate(policy_name, detected_cats, p_class, reid_risk)
        if pol_eval["gate_result"] == "BLOCK":
            gate_result = "BLOCK"
            findings.append({"rule": "POLICY_BLOCK", "severity": "HIGH", "detail": pol_eval["reason"]})

        # Persist llm_requests respecting CHECK constraint:
        # CHECK (prompt_text IS NULL OR gate_result = 'PASS')
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        saved_prompt_text = prompt_text if (gate_result == "PASS" and p_class == "LOCAL") else None

        req_id = f"req_{uuid.uuid4().hex[:12]}"
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO llm_requests (
                    id, provider_id, document_version_id, prompt_hash, prompt_text,
                    gate_result, gate_findings_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    req_id,
                    provider_id,
                    document_version_id,
                    prompt_hash,
                    saved_prompt_text,
                    gate_result,
                    json.dumps(findings),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        self.audit_manager.append(
            "PRIVACY_GATE",
            f"PREFLIGHT_{gate_result}",
            "LLM_REQUEST",
            req_id,
            input_hash=prompt_hash,
            risk="HIGH" if gate_result != "PASS" else "LOW",
            detail={"provider_id": provider_id, "gate_result": gate_result, "findings": findings},
        )

        return {
            "request_id": req_id,
            "gate_result": gate_result,
            "provider_id": provider_id,
            "provider_class": p_class,
            "findings": findings,
        }
