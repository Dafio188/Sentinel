import json
from typing import Any, Dict, List, Optional

class LLMDetector:
    def process_pass(self, text: str, existing_spans: List[Dict[str, Any]], mock_response: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Semantic detection pass using LLM Gemma.
        Re-aligns text_quote with original text to eliminate hallucinated quotes.
        """
        detected: List[Dict[str, Any]] = []
        raw_output = mock_response if mock_response is not None else []

        for item in raw_output:
            quote = item.get("text_quote", "")
            if not quote or quote not in text:
                # Anti-hallucination guard: quote not found in exact text -> discard
                continue

            start_idx = text.find(quote)
            end_idx = start_idx + len(quote)

            detected.append({
                "entity_type": item.get("entity_type", "INDIRECT_IDENTIFIER"),
                "category": item.get("category", "INDIRECT"),
                "detector": "LLM",
                "confidence": float(item.get("confidence", 0.75)),
                "span_start": start_idx,
                "span_end": end_idx,
                "value": quote,
                "action": "MASK",
                "action_reason": item.get("reason", "Rilevamento semantico LLM"),
            })

        return detected
