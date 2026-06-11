from pathlib import Path
import json


def load_published_titles(data_path: Path) -> list[str]:
    if not data_path.exists():
        return []
    return json.loads(data_path.read_text(encoding="utf-8"))
