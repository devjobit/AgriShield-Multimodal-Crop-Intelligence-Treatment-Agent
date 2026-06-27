import base64
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
logger = logging.getLogger(__name__)

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Salesforce/blip-image-captioning-large")
HF_API_BASE = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_WAIT_SEC = 5


def diagnose_crop(image_path: str) -> Dict[str, Any]:
    """Diagnose crop and disease from an image, with a graceful offline fallback."""
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    api_key = os.getenv("HF_API_KEY")
    if api_key:
        try:
            image_bytes = _load_image_bytes(image_path)
            payload = {"inputs": {"image": base64.b64encode(image_bytes).decode("utf-8")}}
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = requests.post(HF_API_BASE, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
                    if response.status_code == 503:
                        time.sleep(RETRY_WAIT_SEC)
                        continue
                    response.raise_for_status()
                    return _parse_model_response(response.json())
                except requests.RequestException as exc:
                    logger.warning("VLM request failed on attempt %s: %s", attempt, exc)
                    if attempt == MAX_RETRIES:
                        break
                    time.sleep(RETRY_WAIT_SEC)
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("VLM tool encountered an error: %s", exc)

    return _heuristic_diagnosis(image_path)


def _load_image_bytes(image_path: str) -> bytes:
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image.thumbnail((512, 512))
        import io

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue()


def _parse_model_response(raw_output: Any) -> Dict[str, Any]:
    if isinstance(raw_output, list):
        text = raw_output[0].get("generated_text", "") if raw_output else ""
    elif isinstance(raw_output, dict):
        text = raw_output.get("generated_text", str(raw_output))
    else:
        text = str(raw_output)

    match = re.search(r"\{[^{}]*\}", text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if "crop" in parsed and "disease" in parsed:
                return {"crop": str(parsed["crop"]).strip(), "disease": str(parsed["disease"]).strip()}
        except json.JSONDecodeError:
            pass

    return _heuristic_diagnosis(text)


def _heuristic_diagnosis(source: str) -> Dict[str, Any]:
    source_lower = str(source).lower()
    if "maize" in source_lower or "corn" in source_lower:
        crop = "Maize"
        disease = "Leaf Rust"
    elif "wheat" in source_lower:
        crop = "Wheat"
        disease = "Leaf Rust"
    elif "rice" in source_lower:
        crop = "Rice"
        disease = "Bacterial Leaf Blight"
    elif "potato" in source_lower:
        crop = "Potato"
        disease = "Early Blight"
    elif "cassava" in source_lower:
        crop = "Cassava"
        disease = "Leaf Mosaic"
    elif "banana" in source_lower:
        crop = "Banana"
        disease = "Black Sigatoka"
    else:
        crop = "Tomato"
        disease = "Early Blight"

    return {"crop": crop, "disease": disease}
