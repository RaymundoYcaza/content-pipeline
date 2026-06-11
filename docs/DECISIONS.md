# DECISIONS

## ADR-0001
Se adopta Python como orquestador determinista del pipeline.

## ADR-0002
La IA será invocada como capacidad puntual por etapa, no como controlador del flujo.

## ADR-0003
Se adopta Typer para la CLI.

## ADR-0004
Se adopta frontmatter YAML como fuente primaria de estado para cada nota Markdown.

## ADR-0005
Se soportan dos proveedores: Ollama y OpenRouter.

## ADR-0006
Se adopta embeddings vía API para similitud semántica; el cálculo del score se realiza en Python.
