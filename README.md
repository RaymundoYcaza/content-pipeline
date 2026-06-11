# Content Pipeline

Pipeline determinista de creación de contenido asistido por IA.

## Objetivo

Python controla estado, validaciones, rutas, similitud, retries y delays. La IA actúa como función inteligente en etapas definidas del pipeline.

## Stack inicial

- Python 3.11+
- Typer para CLI
- Frontmatter YAML en archivos Markdown
- Ollama y OpenRouter como proveedores configurables
- Embeddings vía API para similitud semántica

## Windows 10 quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
copy .env.example .env
pipeline doctor
pipeline state
```

## Estructura de stages

- propuestas
- temas
- en_redaccion
- en_edicion
- revision_humana
- descartados
- publicados
