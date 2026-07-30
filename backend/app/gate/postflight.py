import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from backend.app.audit.chain import AuditChainManager
from backend.app.db.engine import get_db_connection
from backend.app.privacy.recognizers import DeterministicDetector

class PostflightScanner:
    def __init__(self):
        self.detector = DeterministicDetector()
        self.audit_manager = AuditChainManager()

    def scan_response(self, request_id: str, response_text: str, latency_ms: int = 100) -> Dict[str, Any]:
        findings = self.detector.scan(response_text)
        postflight_result = "CLEAN"
        reid_warning = False

        high_conf_pii = [f for f in findings if f.get("confidence", 0.0) >= 0.70]
        if len(high_conf_pii) > 0:
            has_special = any(f.get("category") == "SPECIAL" for f in high_conf_pii)
            postflight_result = "BLOCKED" if has_special else "LEAK_SUSPECT"

        # Re-identification heuristic v1
        reid_triggers = ["si tratta di", "probabilmente è", "corrisponde a"]
        if any(trig in response_text.lower() for trig in reid_triggers):
            reid_warning = True

        response_id = f"resp_{uuid.uuid4().hex[:12]}"
        findings_json = json.dumps({"pii_findings": high_conf_findings if 'high_conf_findings' in locals() else high_conf_pii, "reid_warning": reid_warning})

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO llm_responses (
                    id, request_id, response_text, postflight_result,
                    postflight_findings_json, latency_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response_id,
                    request_id,
                    response_text,
                    postflight_result,
                    findings_json,
                    latency_ms,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        self.audit_manager.append(
            "PRIVACY_GATE",
            f"POSTFLIGHT_{postflight_result}",
            "LLM_RESPONSE",
            response_id,
            risk="HIGH" if postflight_result != "CLEAN" else "LOW",
            detail={"postflight_result": postflight_result, "reid_warning": reid_warning},
        )

        return {
            "response_id": response_id,
            "request_id": request_id,
            "postflight_result": postflight_result,
            "reid_warning": reid_warning,
            "response_text": response_text,
        }
