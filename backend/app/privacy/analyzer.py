import hashlib
import hmac
from typing import Any, Dict, List, Optional
from backend.app.privacy.parsers.base import ParsedDocument
from backend.app.privacy.recognizers import DeterministicDetector

class AnalyzerEngine:
    def __init__(self, secret_salt: str = "aigate_local_salt"):
        self.detector = DeterministicDetector()
        self.secret_salt = secret_salt

    def _hash_value(self, val: str) -> str:
        return hmac.new(
            self.secret_salt.encode("utf-8"),
            val.strip().upper().encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def analyze(self, parsed_doc: ParsedDocument) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []

        # 1. Run deterministic detector on parsed text
        raw_entities = self.detector.scan(parsed_doc.text)
        for ent in raw_entities:
            ent["value_hash"] = self._hash_value(ent["value"])
            entities.append(ent)

        # 2. Append document METADATA as detected_entities (detector='METADATA')
        for meta in parsed_doc.metadata:
            val = meta.get("value", "")
            entities.append({
                "entity_type": meta.get("entity_type", "METADATA"),
                "category": meta.get("category", "IDENTIFIER"),
                "detector": "METADATA",
                "confidence": 0.99,
                "span_start": None,
                "span_end": None,
                "value": val,
                "value_hash": self._hash_value(val),
                "action": "REMOVE",
                "action_reason": f"Metadato sanitizzato dall'export ({meta.get('field', 'meta')})",
            })

        return entities
