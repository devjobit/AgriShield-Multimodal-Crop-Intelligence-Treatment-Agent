from typing import Any, Dict


def interpret_diagnosis(diagnosis: Dict[str, Any]) -> Dict[str, Any]:
    crop = str(diagnosis.get("crop", "Unknown")).strip() or "Unknown"
    disease = str(diagnosis.get("disease", "Unknown")).strip() or "Unknown"
    severity = "moderate"
    if any(token in disease.lower() for token in ["blight", "rust", "rot", "wilt"]):
        severity = "moderate"
    elif disease.lower() in {"healthy", "healthy plant"}:
        severity = "low"

    return {
        "crop": crop.capitalize(),
        "disease": disease.capitalize(),
        "severity": severity,
        "confidence": "medium",
        "summary": f"The crop appears to be {crop.capitalize()} with {disease.capitalize()} symptoms.",
    }
