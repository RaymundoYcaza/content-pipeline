# Content Pipeline v0.2.0

## Resumen

Este proyecto implementa un pipeline determinista de creación de contenido asistido por IA. Python controla el flujo, valida reglas, calcula similitud, actualiza frontmatter y mueve archivos entre carpetas por etapa. La IA se usa como función especializada en agentes puntuales: Bea, Isabela, David y Basilio.

## Filosofía

- Python orquesta, la IA ejecuta tareas acotadas.
- El estado vive en archivos Markdown con frontmatter YAML.
- Toda evolución importante comienza por una spec con timestamp.
- Cada cambio debe reflejarse en changelog, estado del sistema y versión.
- Las reglas de cada agente se editan fuera del código, en archivos Markdown bajo `rules/`.

## Pipeline editorial v1

### Etapas

1. `propuestas`
2. `temas`
3. `en_redaccion`
4. `en_edicion`
5. `revision_humana`
6. `publicados`
7. `descartados`

### Agentes

| Agente | Entrada | Salida | Propósito |
|---|---|---|---|
| Bea | `propuestas` | `temas` o `descartados` | filtra similitud y valida propuesta |
| Isabela | `temas` | `en_redaccion` | genera estructura editorial |
| David | `en_redaccion` | `en_edicion` | redacta borrador completo |
| Basilio | `en_edicion` | `revision_humana` | edita y deja listo para revisión humana |

## Estado actual

### Implementado

- CLI con Typer
- Configuración central en YAML
- Soporte para Ollama y OpenRouter
- Embeddings para similitud
- Retry/backoff básico
- Prompts externos en `rules/`
- Agentes v1: Bea, Isabela, David, Basilio
- Validaciones deterministas mínimas
- Movimiento de archivos por etapa
- Tests de harness básicos
- modo loop explícito desde CLI
- throttling configurable entre llamadas, etapas y ciclos
- epera en vacío para operación continua
- observabilidad básica por ciclo

### No implementado

- Publicación
- Historial de versiones de contenido
- Cola de revisión humana con checklist formal
- Fallback automático de proveedor
- Indexación persistente de embeddings

## Estructura recomendada del repositorio

```text
content-pipeline/
├── specs/
├── docs/
├── config/
├── content/
├── rules/
├── examples/
├── data/
├── pipeline/
├── tests/
└── pyproject.toml
```

## Contratos del sistema

### Estado por frontmatter

Campos mínimos esperados:

- `title`
- `stage`
- `stage_status`
- `created`
- `updated`

Campos recomendados:

- `agent`
- `category`
- `similarity_score`
- `rejection_reason`
- `revision_notes`
- `source_keywords`
- `canonical_slug`

### Reglas generales

- Ningún agente debe depender de prompts hardcodeados.
- Cada agente debe leer sus reglas desde `rules/<agente>/` y `rules/shared/`.
- Python valida y decide transición de estados.
- Si una salida no cumple validación, la nota no debe avanzar de etapa.

## Instructivo para retomar el proyecto

1. Activar entorno virtual.
2. Revisar `docs/SYSTEM_STATE.md` y `docs/CHANGELOG.md`.
3. Revisar la spec más reciente en `specs/`.
4. Verificar versión actual en `docs/VERSIONING.md` y tag Git más reciente.
5. Ejecutar `pipeline doctor` y `pipeline state`.
6. Continuar desde el stage o feature pendiente.

## Instructivo para LLMs

Un LLM que continúe este proyecto debe leer primero:

1. `docs/PROJECT_STATE_V1.md`
2. `docs/HARNESS_RULES.md`
3. `docs/SPECS_CONVENTION.md`
4. `docs/VERSIONING.md`
5. `docs/PERPLEXITY_SPACE_SETUP.md`
6. La spec más reciente en `specs/`

## Próximas evoluciones sugeridas

- Slice de revisión humana asistida
- Slice de publicación
- Versionado semántico del contenido
- Historial de cambios por nota
- Persistencia de embeddings
