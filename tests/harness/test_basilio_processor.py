from pathlib import Path
from types import SimpleNamespace
import frontmatter

from pipeline.agents.basilio import BasilioProcessor


class FakeClient:
    def chat(self, messages):
        return """# Cómo organizar un pipeline de contenido con IA

## Introducción
Texto editado.

## Desarrollo
### Sección 1
Texto editado.

### Sección 2
Texto editado.

## Cierre
Texto editado.
"""


class FakeRouter:
    def __init__(self, _config):
        pass

    def text_client(self):
        return FakeClient()


def test_basilio_moves_note_to_revision_humana(tmp_path: Path, monkeypatch):
    content_root = tmp_path / "content"
    for folder in ["en_edicion", "revision_humana"]:
        (content_root / folder).mkdir(parents=True, exist_ok=True)

    note_path = content_root / "en_edicion" / "note.md"
    post = frontmatter.loads(
        """---
title: Cómo organizar un pipeline de contenido con IA
category: guia
stage: en_edicion
stage_status: approved
created: x
updated: x
---
# Cómo organizar un pipeline de contenido con IA

## Introducción
Texto base.

## Desarrollo
### Sección 1
Texto base.

### Sección 2
Texto base.

## Cierre
Texto base.
"""
    )
    note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    config = SimpleNamespace(project=SimpleNamespace(content_root=str(content_root)))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("pipeline.agents.basilio.ProviderRouter", FakeRouter)

    results = BasilioProcessor(config).run()
    assert results[0]["decision"] == "approved"
    assert (content_root / "revision_humana" / "note.md").exists()