from pathlib import Path

from rag.db import load_records


def ingest_csv(csv_path: str | None = None):
    path = Path(csv_path) if csv_path else None
    return load_records(path)
