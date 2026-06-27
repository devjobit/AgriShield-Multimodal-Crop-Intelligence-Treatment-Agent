from typing import Any, Dict


def evaluate_retrieval(result: Dict[str, Any], expected_disease: str | None = None) -> Dict[str, Any]:
    score = 8.0
    reasons = []
    if result.get("similarity_score", 0) >= 0.8:
        score += 1.0
        reasons.append("Strong semantic match")
    elif result.get("similarity_score", 0) >= 0.5:
        reasons.append("Reasonable match")
    else:
        score -= 1.0
        reasons.append("Match confidence is low")

    if not result.get("treatment"):
        score -= 2.0
        reasons.append("No treatment returned")

    if expected_disease and expected_disease.lower() in str(result.get("disease", "")).lower():
        reasons.append("Disease matched expected label")
    else:
        reasons.append("Disease label did not fully match")

    return {
        "score": round(max(0, min(10, score)), 1),
        "reason": "; ".join(reasons),
    }
