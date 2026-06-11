from pathlib import Path


def collect_state(content_root: Path) -> dict[str, int]:
    stages = [
        "propuestas",
        "temas",
        "en_redaccion",
        "en_edicion",
        "revision_humana",
        "descartados",
        "publicados",
    ]
    summary = {}
    for stage in stages:
        folder = content_root / stage
        summary[stage] = len(list(folder.glob("*.md"))) if folder.exists() else 0
    return summary
