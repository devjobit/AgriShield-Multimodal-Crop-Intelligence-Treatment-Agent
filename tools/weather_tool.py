import logging
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT_SECONDS = 10


def get_weather(city: str) -> Dict[str, Any]:
    """Fetch weather data for a city, with a deterministic fallback if no API key is available."""
    city = (city or "Nairobi").strip() or "Nairobi"
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key:
        try:
            params = {"q": city, "appid": api_key, "units": "metric"}
            response = requests.get(WEATHER_API_BASE, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()
            temperature = float(data.get("main", {}).get("temp", 25.0))
            humidity = int(data.get("main", {}).get("humidity", 60))
            description = str(data.get("weather", [{}])[0].get("description", "clear sky")).capitalize()
            rain_probability = _estimate_rain_probability(description)
            return {
                "temperature": round(temperature, 1),
                "humidity": humidity,
                "rain_probability": rain_probability,
                "description": description,
            }
        except requests.RequestException as exc:
            logger.warning("Weather lookup failed: %s", exc)

    return _heuristic_weather(city)


def _estimate_rain_probability(description: str) -> float:
    desc = description.lower()
    if any(token in desc for token in ["rain", "drizzle", "storm", "thunder", "shower"]):
        return 0.7
    if any(token in desc for token in ["cloud", "mist", "fog"]):
        return 0.3
    return 0.1


def _heuristic_weather(city: str) -> Dict[str, Any]:
    city_lower = city.lower()
    if "nairobi" in city_lower:
        temperature = 24.0
        humidity = 78
        description = "light rain"
    elif "pune" in city_lower:
        temperature = 29.0
        humidity = 62
        description = "clear sky"
    elif "lagos" in city_lower:
        temperature = 30.0
        humidity = 82
        description = "humid"
    else:
        temperature = 26.0
        humidity = 65
        description = "partly cloudy"
    return {
        "temperature": temperature,
        "humidity": humidity,
        "rain_probability": _estimate_rain_probability(description),
        "description": description,
    }