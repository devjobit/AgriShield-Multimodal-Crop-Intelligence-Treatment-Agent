from typing import Any, Dict


def interpret_treatment(diagnosis: Dict[str, Any], treatment: Dict[str, Any]) -> Dict[str, Any]:
    disease_name = diagnosis.get("disease", "Unknown")
    treatment_text = treatment.get("treatment", "Inspect the crop and contact a local agronomy extension officer.")
    similarity = float(treatment.get("similarity_score", 0.5))

    return {
        "crop": diagnosis.get("crop", "Unknown"),
        "disease": disease_name,
        "treatment": treatment_text,
        "similarity_score": similarity,
        "notes": "Prefer early intervention and follow label instructions when using any chemical product.",
    }
