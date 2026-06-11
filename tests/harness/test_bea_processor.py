from pathlib import Path
from types import SimpleNamespace
import frontmatter

from pipeline.agents.bea import BeaProcessor


class FakeEmbeddingService:
    def __init__(self, _config):
        pass

    def embed(self, texts):
        mapping = {
            "Cómo crear procesos editoriales repetibles": [1.0, 0.0],
            "Automatización de tareas de redacción con IA": [0.9, 0.1],
            "Diseño de flujos de trabajo para contenido técnico": [0.8, 0.2],
            "Cómo organizar un pipeline de contenido con IA": [1.0, 0.0],
        }
        return [mapping[t] for t in texts]


def test_bea_rejects_high_similarity(tmp_path: Path, monkeypatch):
    content_root = tmp_path / "content"
    for folder in ["propuestas", "temas", "descartados"]:
        (content_root / folder).mkdir(parents=True, exist_ok=True)

    note_path = content_root / "propuestas" / "note.md"
    post = frontmatter.loads(
        """---\ntitle: Cómo organizar un pipeline de contenido con IA\nstage: propuestas\nstage_status: pending\ncreated: x\nupdated: x\n---\nBody"
    )
    note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "published_titles.json").write_text(
        '["Cómo crear procesos editoriales repetibles"]', encoding="utf-8"
    )

    config = SimpleNamespace(
        project=SimpleNamespace(content_root=str(content_root)),
        similarity=SimpleNamespace(review_threshold=0.72, reject_threshold=0.84),
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("pipeline.agents.bea.EmbeddingService", FakeEmbeddingService)

    results = BeaProcessor(config).run()
    assert results[0]["decision"] == "reject"
    assert (content_root / "descartados" / "note.md").exists()
