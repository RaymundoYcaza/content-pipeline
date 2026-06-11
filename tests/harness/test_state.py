from pathlib import Path
from pipeline.core.state import collect_state


def test_collect_state(tmp_path: Path):
    (tmp_path / "propuestas").mkdir()
    (tmp_path / "propuestas" / "a.md").write_text("x", encoding="utf-8")
    summary = collect_state(tmp_path)
    assert summary["propuestas"] == 1
