from typing import Any, Dict, List

CATEGORY_WEIGHT = {
    "SPECIAL": 4,
    "IDENTIFIER": 3,
    "FINANCIAL": 2,
    "INDIRECT": 1,
}

DETECTOR_WEIGHT = {
    "REGEX": 4,
    "METADATA": 4,
    "OCR": 3,
    "DICT": 2,
    "NER": 2,
    "LLM": 1,
}

class MergeEngine:
    def merge(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Filter confidence < 0.50
        filtered = [e for e in entities if e.get("confidence", 0.0) >= 0.50]
        
        # Sort by start span, then by length descending
        span_entities = [e for e in filtered if e.get("span_start") is not None]
        non_span_entities = [e for e in filtered if e.get("span_start") is None]

        merged_spans: List[Dict[str, Any]] = []
        for current in sorted(span_entities, key=lambda x: (x["span_start"], -x["span_end"])):
            overlap_found = False
            for prev in merged_spans:
                # Check for overlap: [start, end]
                if not (current["span_end"] <= prev["span_start"] or current["span_start"] >= prev["span_end"]):
                    overlap_found = True
                    # Compare category severity first
                    curr_cat_w = CATEGORY_WEIGHT.get(current["category"], 0)
                    prev_cat_w = CATEGORY_WEIGHT.get(prev["category"], 0)

                    if curr_cat_w > prev_cat_w:
                        winner = current
                    elif curr_cat_w < prev_cat_w:
                        winner = prev
                    else:
                        # Tie: compare detector reliability
                        curr_det_w = DETECTOR_WEIGHT.get(current["detector"], 0)
                        prev_det_w = DETECTOR_WEIGHT.get(prev["detector"], 0)
                        winner = current if curr_det_w >= prev_det_w else prev

                    # Replace winner in merged_spans
                    merged_spans.remove(prev)
                    merged_spans.append(winner)
                    break

            if not overlap_found:
                merged_spans.append(current)

        final_list = merged_spans + non_span_entities

        # Assign REVIEW status based on thresholds
        for ent in final_list:
            conf = ent.get("confidence", 1.0)
            det = ent.get("detector", "")
            if (0.50 <= conf < 0.70) or (det == "LLM" and conf < 0.70) or ent.get("entity_type") == "UNCERTAIN_PII":
                ent["action"] = "REVIEW"
                ent["action_reason"] = "Azione in sospeso per revisione umana (soglia confidence/LLM/OCR)"

        return final_list
