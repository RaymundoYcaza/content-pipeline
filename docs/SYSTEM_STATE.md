# SYSTEM_STATE

## Versión objetivo
0.3.0

## Resumen actual
El pipeline mantiene su filosofía determinista: Python orquesta, las reglas viven fuera del código y la IA opera como función especializada por etapa. La nueva capa de voz editorial ya fue definida como contrato de reglas para mantener consistencia entre borrador, edición y revisión humana.

## Estado del sistema

### Implementado
- CLI con Typer.
- Configuración central en YAML.
- Soporte para Ollama y OpenRouter.
- Embeddings para similitud.
- Retry/backoff básico.
- Prompts externos en `rules/`.
- Agentes v1: Bea, Isabela, David y Basilio.
- Validaciones deterministas mínimas.
- Movimiento de archivos por etapa.
- Tests de harness básicos.
- Modo loop explícito desde CLI.
- Throttling configurable entre llamadas, etapas y ciclos.
- Espera en vacío para operación continua.
- Observabilidad básica por ciclo.
- Capa editorial de voz definida en reglas compartidas.
- Matriz por etapa para modular cercanía, contundencia y formalidad.
- Validador determinista de voz editorial (`voice_validator.py`).
- Checklist formal de revisión humana en `rules/revision_humana/checklist.md`.
- David lee `depth_profile` del frontmatter de cada nota para override de profundidad.
- David y Basilio cargan `author_voice.md` en sus prompts.
- Isabela recibe restricciones duras de voz en su input.
- Validación editorial por Basilio antes de promover a `revision_humana`.
- Lector de `hook_requirements` del config en el validador de apertura.

### En progreso
- Pruebas funcionales de la capa de voz con al menos tres casos: pieza formal, tutorial y publicación breve.
- Integración de `voice_validator.py` en el flujo de David y Basilio para validación dura de voz.

### Pendiente
- Publicación.
- Historial de versiones de contenido.
- Cola de revisión humana con checklist formal.
- Fallback automático de proveedor.
- Indexación persistente de embeddings.
- Pruebas funcionales de la nueva capa de voz.

## Contratos del sistema
- Ningún agente debe depender de prompts hardcodeados.
- Cada agente debe leer sus reglas desde `rules/<agente>/` y `rules/shared/`.
- Python valida y decide transición de estados.
- Si una salida no cumple validación, la nota no debe avanzar de etapa.

## Próximo paso
Ejecutar pruebas de contenido con al menos tres casos: pieza formal, tutorial/guía y publicación breve, para validar la matriz de voz y los bloqueos normativos.