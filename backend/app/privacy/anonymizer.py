import json
from typing import Any, Dict, List, Optional, Tuple
from backend.app.privacy.generalize import generalize_value
from backend.app.vault.manager import VaultLockedError, VaultManager

class AnonymizerEngine:
    def __init__(self, vault_manager: Optional[VaultManager] = None):
        self.vault_manager = vault_manager

    def anonymize(
        self,
        text: str,
        entities: List[Dict[str, Any]],
        strategy: str,
        document_id: str,
        vault_unlocked: bool = True,
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Applies anonymization strategy (MASK, REPLACE, GENERALIZE, REMOVE, SEMANTIC).
        Returns (protected_text, kind, diff_json_list)
        """
        if strategy == "REPLACE":
            if not vault_unlocked or self.vault_manager is None or self.vault_manager.is_locked():
                raise VaultLockedError("VaultLockedError: REPLACE strategy requires an unlocked Vault.")

        # Sort entities by span_start descending to replace text without index drift
        span_entities = sorted(
            [e for e in entities if e.get("span_start") is not None],
            key=lambda x: x["span_start"],
            reverse=True,
        )

        protected_text = text
        diff_list: List[Dict[str, Any]] = []
        counters: Dict[str, int] = {}

        kind = "MASKED"
        if strategy == "REPLACE":
            kind = "PSEUDONYMIZED"
        elif strategy == "SEMANTIC":
            kind = "SEMANTIC"

        for ent in span_entities:
            val = ent.get("value", "")
            e_type = ent.get("entity_type", "PII")
            start = ent["span_start"]
            end = ent["span_end"]

            replacement = f"[{e_type}]"

            if strategy == "MASK":
                replacement = f"[{e_type}]"
            elif strategy == "REPLACE":
                counters[e_type] = counters.get(e_type, 0) + 1
                token = f"{e_type}_{counters[e_type]:03d}"
                replacement = token
                if self.vault_manager:
                    self.vault_manager.store_pseudonym(token, document_id, e_type, val)
            elif strategy == "GENERALIZE":
                replacement = generalize_value(e_type, val)
            elif strategy == "REMOVE":
                replacement = "[RIMOSSO]"
            elif strategy == "SEMANTIC":
                replacement = f"[{e_type}_GENERALIZZATO]"

            # Perform string slicing replacement
            protected_text = protected_text[:start] + replacement + protected_text[end:]

            diff_list.append({
                "original": val,
                "replacement": replacement,
                "entity_type": e_type,
                "strategy": strategy,
            })

        return protected_text, kind, diff_list
