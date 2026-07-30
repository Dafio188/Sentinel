from typing import Any, Dict, List, Optional

class PolicyEngine:
    def evaluate(
        self,
        policy_name: str,
        detected_categories: List[str],
        provider_class: str,
        reid_risk: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Evaluates policy (STRICT, BALANCED, CUSTOM) against payload categories and provider privacy class.
        Returns {"gate_result": PASS|REVIEW|BLOCK, "action": ..., "reason": ...}
        """
        policy = policy_name.upper()

        if provider_class == "LOCAL":
            return {"gate_result": "PASS", "action": "ALLOW", "reason": "Provider locale: nessun blocco di policy"}

        if policy == "STRICT":
            if len(detected_categories) > 0:
                return {
                    "gate_result": "BLOCK",
                    "action": "BLOCK",
                    "reason": "Policy STRICT: rilevati dati personali verso provider esterno",
                }

        if policy == "BALANCED" or policy == "CUSTOM":
            if "SPECIAL" in detected_categories:
                return {
                    "gate_result": "BLOCK",
                    "action": "BLOCK",
                    "reason": "Dati particolari (SPECIAL) non inviabili a provider non-LOCAL",
                }
            if "IDENTIFIER" in detected_categories or "FINANCIAL" in detected_categories:
                return {
                    "gate_result": "REVIEW",
                    "action": "MASK",
                    "reason": "Dati identificativi/finanziari presenti: richiede anonimizzazione prima dell'invio",
                }
            if "INDIRECT" in detected_categories:
                return {
                    "gate_result": "PASS",
                    "action": "WARN",
                    "reason": "Identificatori indiretti presenti: pre-flight passato con avviso",
                }

        return {"gate_result": "PASS", "action": "ALLOW", "reason": "Policy verificata con successo"}
