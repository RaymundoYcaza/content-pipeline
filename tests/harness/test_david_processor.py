from pathlib import Path
from types import SimpleNamespace
import frontmatter

from pipeline.agents.david import DavidProcessor


class FakeClient:
    def chat(self, messages):
        return """# Cómo organizar un pipeline de contenido con IA

## Introducción
Un pipeline de contenido con IA permite reducir el tiempo dedicado a las primeras fases de ideación y borrador. Para que funcione bien, debe estar controlado por reglas claras y por un orquestador determinista que valide cada transición.

## Desarrollo
### Sección 1
La primera capa del sistema debe encargarse de la validación de entradas, del control de estado y del movimiento de archivos entre carpetas. Esto permite que cada nota tenga una trazabilidad clara y que el proceso sea auditable.

La integración con IA debe verse como una capacidad puntual y no como el cerebro del sistema. De ese modo, Python conserva la responsabilidad de validar, medir similitud, aplicar thresholds y decidir el siguiente paso.

### Sección 2
La redacción debe apoyarse en un esquema aprobado previamente. Eso reduce la deriva del modelo y facilita que el contenido final mantenga un orden lógico desde la introducción hasta el cierre.

Además, la edición posterior puede centrarse en calidad y estilo, no en corregir una estructura deficiente. Esto mejora la velocidad del pipeline y hace más fácil incorporar revisión humana al final.

## Cierre
Un enfoque por etapas reduce errores y facilita la evolución del sistema. Cuando cada agente trabaja con contratos y reglas editables, el pipeline puede crecer sin perder control.
"""


class FakeRouter:
    def __init__(self, _config):
        pass

    def text_client(self):
        return FakeClient()


def test_david_moves_note_to_en_edicion(tmp_path: Path, monkeypatch):
    content_root = tmp_path / "content"
    for folder in ["en_redaccion", "en_edicion"]:
        (content_root / folder).mkdir(parents=True, exist_ok=True)

    note_path = content_root / "en_redaccion" / "note.md"
    post = frontmatter.loads(
        """---\ntitle: Cómo organizar un pipeline de contenido con IA\ncategory: guia\nstage: en_redaccion\nstage_status: approved\ncreated: x\nupdated: x\n---\n# Cómo organizar un pipeline de contenido con IA\n\n## Introducción\n- Punto clave\n\n## Desarrollo\n### Sección 1\n- Punto clave\n\n### Sección 2\n- Punto clave\n\n## Cierre\n- Punto clave\n"""
    )
    note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    config = SimpleNamespace(project=SimpleNamespace(content_root=str(content_root)))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("pipeline.agents.david.ProviderRouter", FakeRouter)

    results = DavidProcessor(config).run()
    assert results[0]["decision"] == "approved"
    assert (content_root / "en_edicion" / "note.md").exists()
