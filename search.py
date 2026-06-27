import difflib
from typing import Dict, List

from rag.db import load_records


def retrieve_treatment(disease_name: str) -> Dict[str, object]:
    records = load_records()
    disease_query = (disease_name or "").strip().lower()

    if not disease_query:
        return _fallback_result("Unknown disease")

    exact_matches = [record for record in records if disease_query in record["disease"].lower()]
    if exact_matches:
        best = exact_matches[0]
        return _build_result(best, 0.95)

    scored = []
    for record in records:
        score = difflib.SequenceMatcher(None, disease_query, record["disease"].lower()).ratio()
        scored.append((score, record))
    scored.sort(key=lambda item: item[0], reverse=True)

    if scored and scored[0][0] >= 0.35:
        score, best = scored[0]
        return _build_result(best, score)

    return _fallback_result(disease_name)


def _fallback_result(disease_name: str) -> Dict[str, object]:
    return {
        "crop": "Unknown",
        "disease": disease_name or "Unknown disease",
        "treatment": "Inspect the field closely and contact a local extension service for a verified treatment recommendation.",
        "similarity_score": 0.2,
    }


def _build_result(record: Dict[str, str], score: float) -> Dict[str, object]:
    return {
        "crop": record.get("crop", "Unknown"),
        "disease": record.get("disease", "Unknown"),
        "treatment": record.get("treatment", "No treatment found."),
        "similarity_score": round(float(score), 2),
    }