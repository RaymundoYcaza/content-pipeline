from pathlib import Path
from types import SimpleNamespace
import frontmatter

from pipeline.agents.isabela import IsabelaProcessor


class FakeClient:
    def chat(self, messages):
        return """# Cómo organizar un pipeline de contenido con IA

## Introducción
- Contexto
- Objetivo

## Desarrollo
### Sección 1
- Punto A
- Punto B

### Sección 2
- Punto C
- Punto D

## Cierre
- Síntesis
- Próximo paso
"""


class FakeRouter:
    def __init__(self, _config):
        pass

    def text_client(self):
        return FakeClient()


def test_isabela_moves_note_to_en_redaccion(tmp_path: Path, monkeypatch):
    content_root = tmp_path / "content"
    for folder in ["temas", "en_redaccion"]:
        (content_root / folder).mkdir(parents=True, exist_ok=True)

    note_path = content_root / "temas" / "note.md"
    post = frontmatter.loads(
        """---
title: Cómo organizar un pipeline de contenido con IA
stage: temas
stage_status: approved
created: x
updated: x
---
Idea base"""
    )
    note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    config = SimpleNamespace(project=SimpleNamespace(content_root=str(content_root)))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("pipeline.agents.isabela.ProviderRouter", FakeRouter)

    results = IsabelaProcessor(config).run()
    assert results[0]["decision"] == "approved"
    assert (content_root / "en_redaccion" / "note.md").exists()
