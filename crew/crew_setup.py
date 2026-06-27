import json
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from agents.agronomist import synthesize_report
from agents.diagnostician import interpret_diagnosis
from agents.researcher import interpret_treatment
from rag.search import retrieve_treatment
from tools.vlm_tool import diagnose_crop
from tools.weather_tool import get_weather

load_dotenv()
logger = logging.getLogger(__name__)


def run_analysis(image_path: Optional[str] = None, location: str = "", diagnosis: Optional[Dict[str, Any]] = None, treatment: Optional[Dict[str, Any]] = None, weather: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the full AgriGuard pipeline using the available tools."""
    if diagnosis is None:
        if image_path is None:
            raise ValueError("Either diagnosis or image_path is required")
        diagnosis = diagnose_crop(image_path)

    if treatment is None:
        treatment = retrieve_treatment(diagnosis.get("disease", ""))

    if weather is None:
        try:
            weather = get_weather(location or "Nairobi")
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("Weather fetch failed: %s", exc)
            weather = {
                "temperature": 25.0,
                "humidity": 60,
                "rain_probability": 0.1,
                "description": "Weather data unavailable",
            }

    cleaned_diagnosis = interpret_diagnosis(diagnosis)
    cleaned_treatment = interpret_treatment(cleaned_diagnosis, treatment)
    final_result = synthesize_report(cleaned_diagnosis, cleaned_treatment, weather, location)

    return {
        "crop": final_result.get("crop", cleaned_diagnosis.get("crop", "Unknown")),
        "disease": final_result.get("disease", cleaned_diagnosis.get("disease", "Unknown")),
        "treatment": final_result.get("treatment", cleaned_treatment.get("treatment", treatment.get("treatment", "N/A"))),
        "weather_summary": final_result.get("weather_summary", f"{weather.get('description', 'N/A')} at {weather.get('temperature', 'N/A')}°C"),
        "final_recommendation": final_result.get("final_recommendation", "No recommendation generated."),
    }
