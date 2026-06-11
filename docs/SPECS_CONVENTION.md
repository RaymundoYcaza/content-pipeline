# Specs Convention

## Convención de nombres

Formato obligatorio:

`YYYYMMDDThhmmss_descripcion-kebab-case.md`

Ejemplos:

- `20260611T015600_project-charter.md`
- `20260611T115000_isabela-v1.md`
- `20260611T120700_david-v1.md`

## Objetivo de las specs

Las specs son el contrato de diseño antes de implementación. No son notas informales. Deben permitir que un humano o LLM entienda por qué existe un cambio, qué modifica y cómo validarlo.

## Secciones obligatorias

- `# Título`
- `## Objetivo`
- `## Alcance`
- `## No alcance`
- `## Decisiones`
- `## Implementación`
- `## Validación`
- `## Estado de tareas`

## Estado de tareas

Cada spec debe contener su propio control de avance:

```md
## Estado de tareas
- [ ] diseñar
- [ ] implementar
- [ ] validar
- [ ] documentar
- [ ] actualizar versión
```

## Regla de cierre

Una spec solo se considera cerrada cuando:

- todas sus tareas están completadas
- changelog fue actualizado
- system state fue actualizado
- versión fue actualizada si correspondía
