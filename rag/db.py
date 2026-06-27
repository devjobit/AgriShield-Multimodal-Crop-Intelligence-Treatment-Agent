import csv
from pathlib import Path
from typing import Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "diseases.csv"


def load_records(csv_path: Path | str | None = None) -> List[Dict[str, str]]:
    path = Path(csv_path) if csv_path else DATA_PATH
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {
                "crop": row.get("crop", "").strip(),
                "disease": row.get("disease", "").strip(),
                "treatment": row.get("treatment", "").strip(),
            }
            for row in csv.DictReader(handle)
        ]
