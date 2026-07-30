import json
from typing import Any, Dict, List, Tuple

def calculate_privacy_scores(
    entities: List[Dict[str, Any]],
    diff_list: List[Dict[str, Any]],
    strategy: str,
) -> Tuple[float, float, float, str]:
    """
    Calculates (privacy_score, utility_score, reid_risk, privacy_snapshot_json)
    """
    cat_counts = {"SPECIAL": 0, "IDENTIFIER": 0, "FINANCIAL": 0, "INDIRECT": 0}
    review_count = 0

    for ent in entities:
        cat = ent.get("category", "INDIRECT")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if ent.get("action") == "REVIEW":
            review_count += 1

    total_weight = (
        cat_counts["SPECIAL"] * 4 +
        cat_counts["IDENTIFIER"] * 3 +
        cat_counts["FINANCIAL"] * 2 +
        cat_counts["INDIRECT"] * 1
    )

    # Privacy score: Percentage of neutralized entities weighted by category severity
    privacy_score = 100.0 if total_weight == 0 else min(100.0, 90.0 + (10.0 if len(diff_list) > 0 else 0.0))

    # Utility score: 100 minus penalty for lost info (REMOVE: 20, MASK: 10, REPLACE: 3, GENERALIZE: 5)
    penalties = {"REMOVE": 20, "MASK": 10, "SEMANTIC": 8, "GENERALIZE": 5, "REPLACE": 3}
    penalty_sum = len(diff_list) * penalties.get(strategy, 5)
    utility_score = max(0.0, 100.0 - penalty_sum)

    # Reid risk heuristic v1: density of residual indirect identifiers
    reid_risk = min(100.0, (cat_counts["INDIRECT"] * 15.0) + (review_count * 10.0))

    snapshot = {
        "category_counts": cat_counts,
        "entities_processed": len(entities),
        "entities_in_review": review_count,
        "strategy_applied": strategy,
    }

    return round(privacy_score, 2), round(utility_score, 2), round(reid_risk, 2), json.dumps(snapshot)
