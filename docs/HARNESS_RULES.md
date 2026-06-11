# Harness Rules

## Objetivo

Definir reglas obligatorias para cualquier LLM que modifique el proyecto, ya sea desde CLI o desde un Space de Perplexity.

## Reglas obligatorias de documentación

Cada cambio debe actualizar como mínimo:

- `docs/CHANGELOG.md`
- `docs/SYSTEM_STATE.md`
- al menos una spec nueva o la spec activa correspondiente en `specs/`
- versión en los archivos correspondientes cuando aplique

Ningún cambio de código se considera completo si no actualiza la documentación de estado.

## Reglas obligatorias de specs

- Toda feature, fix, refactor o cambio de arquitectura debe iniciar con una spec nueva.
- El nombre del archivo de spec debe iniciar con timestamp en formato `YYYYMMDDThhmmss`.
- La spec debe documentar objetivo, alcance, no alcance, decisiones, impactos y plan de validación.
- Cada spec debe incluir una sección `## Estado de tareas` con checklist.

### Plantilla mínima de spec

```md
# Nombre de la spec

## Objetivo

## Alcance

## No alcance

## Decisiones

## Implementación

## Validación

## Estado de tareas
- [ ] tarea 1
- [ ] tarea 2
- [ ] tarea 3
```

## Reglas obligatorias de versionado

- Toda feature debe incrementar versión minor.
- Todo fix debe incrementar versión patch.
- Todo cambio rompiente debe incrementar versión major.
- Toda actualización de versión debe reflejarse en:
  - `pyproject.toml`
  - `docs/VERSIONING.md`
  - `docs/CHANGELOG.md`
  - tag Git correspondiente cuando se haga release

## Reglas obligatorias para prompts

- Las reglas de agentes deben vivir en `rules/`.
- Ningún prompt operativo debe quedar hardcodeado en el código salvo casos mínimos de fallback técnico.
- Todo cambio en prompts debe documentarse en changelog y specs.

## Reglas obligatorias de continuidad

Antes de implementar, el LLM debe leer:

1. `docs/PROJECT_STATE_V1.md`
2. `docs/HARNESS_RULES.md`
3. `docs/SPECS_CONVENTION.md`
4. `docs/VERSIONING.md`
5. spec activa más reciente

## Reglas obligatorias para Perplexity Space y LLM CLI

Tanto el Space como el CLI deben:

- proponer primero la spec del cambio
- actualizar documentación de estado
- actualizar versión cuando corresponda
- dejar instrucciones de commit convencional sugerido
- no cerrar una tarea si no se documentó
