# Versioning

## Esquema

Se usa Semantic Versioning:

- `MAJOR`: cambios rompientes
- `MINOR`: nuevas features compatibles
- `PATCH`: fixes y ajustes compatibles

## Versión actual

- `0.1.0`

## Estado del release actual

`0.1.0` representa el cierre del ciclo editorial v1:

- Bea v1
- Isabela v1
- David v1
- Basilio v1
- transición hasta `revision_humana`

## Reglas de incremento

### Feature

- incrementar `MINOR`
- ejemplo: `0.1.0 -> 0.2.0`

### Fix

- incrementar `PATCH`
- ejemplo: `0.1.0 -> 0.1.1`

### Breaking change

- incrementar `MAJOR`
- ejemplo: `0.1.0 -> 1.0.0`

## Archivos que deben reflejar versión

- `pyproject.toml`
- `docs/VERSIONING.md`
- `docs/CHANGELOG.md`
- release/tag Git
