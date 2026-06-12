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

### En progreso
- Integración definitiva de `rules/shared/author_voice.md` en el flujo operativo.
- Ajuste final de `rules/shared/style.md`, `rules/shared/draft_style.md` y `rules/shared/editing_style.md`.
- Validación de compatibilidad de la voz con piezas formales, tutoriales y publicaciones breves.

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