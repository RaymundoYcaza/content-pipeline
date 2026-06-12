# CHANGELOG

## [0.3.0] - 2026-06-11

### Added
- Nueva capa editorial de voz en `rules/shared/author_voice.md`.
- Separación operativa entre marco general de estilo, estilo de borrador y estilo de edición.
- Matriz de formalidad por tipo de publicación.
- Bloque normativo de frases firma permitidas por contexto.
- Bloque normativo de despedidas permitidas.
- Bloque normativo de frases prohibidas o de baja prioridad.
- Protocolo de validación repetible para LLM.
- Protocolo de validación repetible para revisión humana.

### Changed
- `rules/shared/style.md` ahora funciona como marco universal de claridad y utilidad.
- `rules/shared/draft_style.md` ahora prioriza amplitud, cercanía controlada y desarrollo suficiente.
- `rules/shared/editing_style.md` ahora prioriza precisión, compresión y preservación de la firma sin sobrecarga.

### Notes
- La capa de voz quedó definida a nivel documental.
- Falta ejecutar pruebas de validación y confirmar la integración final en el flujo operativo.

## 2026-06-11 17:51 - Loop mode with conservative throttling
- Se añadió modo de ejecución continua del pipeline mediante loop explícito desde CLI.
- Se añadieron pausas configurables entre llamadas IA, entre etapas y entre ciclos.
- Se incorporó control de espera en vacío para evitar llamadas innecesarias a proveedores IA.
- Se formalizó el manejo de retry/backoff y la política de contención ante rate limit.
- Se actualizó la documentación operativa y la spec activa correspondiente.

## 2026-06-11 01:56 - Initial scaffold
- Se creó el scaffold inicial del proyecto.
- Se definió la estructura spec-first.
- Se añadió CLI base con Typer.
- Se añadieron contratos base para config, router, frontmatter y similitud.

