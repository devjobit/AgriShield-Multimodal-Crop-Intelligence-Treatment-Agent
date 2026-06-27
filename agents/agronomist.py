from typing import Any, Dict


def synthesize_report(diagnosis: Dict[str, Any], treatment: Dict[str, Any], weather: Dict[str, Any], location: str) -> Dict[str, Any]:
    crop = diagnosis.get("crop", "Unknown")
    disease = diagnosis.get("disease", "Unknown")
    treatment_text = treatment.get("treatment", "Seek local agronomy advice")
    weather_desc = weather.get("description", "weather data unavailable")
    temperature = weather.get("temperature", "N/A")
    rain_prob = weather.get("rain_probability", 0.0)

    weather_summary = f"In {location or 'your area'}, conditions are {weather_desc} with {temperature}°C and a rain risk of {int(rain_prob * 100)}%."

    if rain_prob > 0.5:
        advice = f"Delay application if possible until the rain has passed. Keep the field monitored and avoid spraying before heavy rain."
    else:
        advice = f"Conditions look manageable for treatment today. Apply the recommended action promptly and monitor the crop for improvement."

    recommendation = (
        f"For {crop} affected by {disease}, start with {treatment_text}. "
        f"{advice} Remove severely affected leaves if possible, and keep the field clean to reduce spread."
    )

    return {
        "crop": crop,
        "disease": disease,
        "treatment": treatment_text,
        "weather_summary": weather_summary,
        "final_recommendation": recommendation,
    }
