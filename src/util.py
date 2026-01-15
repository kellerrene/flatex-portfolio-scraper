import json
import os
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)

def write_json_file(path: str, data: dict) -> None:
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
