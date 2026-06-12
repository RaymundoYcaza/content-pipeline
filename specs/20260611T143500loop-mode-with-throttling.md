# Loop mode with conservative throttling

## Objetivo

Agregar un modo de ejecución continua del pipeline que permita procesar trabajo en bucle con pausas configurables, especialmente en las etapas que usan IA, para reducir el riesgo de exceder límites conservadores de requests por minuto y mantener el comportamiento determinista del sistema. [file:21][file:17]

## Alcance

Este cambio cubre:

- Un modo de ejecución continua desde la CLI, activable explícitamente, para correr ciclos completos del pipeline con pausas entre ciclos. [file:21]
- La aplicación sistemática de retardos configurables entre llamadas a IA y entre etapas del pipeline, usando la configuración central existente y nuevos campos de runtime. [file:17][file:21]
- Backoff configurable ante rate limit y fallos transitorios, manteniendo compatibilidad con el mecanismo ya previsto de retries y rotación de API key. [file:17]
- Reglas de parada segura, espera en vacío y logging de ciclos para que el pipeline pueda operar como asistente en segundo plano sin descontrolarse. [file:21]
- Compatibilidad con la filosofía actual: Python orquesta, la IA actúa como función especializada por etapa y el estado sigue viviendo en frontmatter y movimiento determinista de archivos. [file:21][file:18]

## No alcance

Este cambio no cubre:

- Paralelismo entre agentes o procesamiento concurrente de múltiples notas en paralelo.
- Reemplazo del modelo determinista actual por un scheduler autónomo basado en eventos externos.
- Cambios de prompts operativos o traslado de lógica de negocio desde Python hacia la IA. [file:21][file:24]
- Persistencia distribuida de colas, locks multi-proceso o coordinación entre múltiples instancias del pipeline.
- Publicación automática, revisión humana asistida, indexación persistente de embeddings o multi-marca, ya identificados como evoluciones futuras separadas. [file:21]

## Decisiones

### 1. El loop será opt-in, no por defecto

La ejecución en bucle debe activarse explícitamente por CLI, por ejemplo con `pipeline run --loop`, para preservar el comportamiento actual de ejecución única y evitar cambios sorpresivos en automatizaciones existentes. [file:21]

### 2. Se mantiene Python como orquestador único

La lógica de espera, backoff, retries, selección de siguiente trabajo y control de ciclo se implementará en Python, sin delegar estas decisiones a prompts ni a agentes IA. Esto preserva el contrato del sistema y la trazabilidad del flujo. [file:21][file:18][file:24]

### 3. El throttling se define en configuración central

Toda política operativa de pausas y backoff debe vivir en `pipeline.yaml`, dentro de `runtime`, para que sea ajustable sin tocar código y consistente con el diseño actual de configuración central. [file:17][file:21]

### 4. El modo conservador será la referencia por defecto

El loop se diseñará para priorizar seguridad operativa frente a velocidad. Si no se configuran valores agresivos, el sistema asumirá pausas suficientemente holgadas entre llamadas, entre etapas y entre ciclos. Esto responde al objetivo de operar “como asistente” sin sobrepasar límites conservadores. [file:17]

### 5. No habrá concurrencia en esta versión

Cada ciclo procesará trabajo de forma secuencial por etapa y por nota, aplicando pausas explícitas entre llamadas y transiciones. Esto reduce complejidad, evita ráfagas accidentales y mantiene el pipeline fácil de auditar. [file:21]

### 6. El loop debe distinguir entre tres tipos de espera

Se distinguen tres tiempos operativos:

- Espera entre llamadas IA dentro de una misma etapa.
- Espera entre etapas/agentes dentro de un mismo ciclo.
- Espera entre ciclos completos cuando el pipeline sigue vivo. [file:17]

### 7. Los rate limits usarán backoff progresivo

Ante errores transitorios o rate limits, el sistema aplicará retry con backoff progresivo basado en `retry_backoff_seconds`, con posibilidad de alternar API key secundaria si la configuración lo permite. Esto extiende el contrato ya insinuado por la configuración actual. [file:17]

### 8. Si no hay trabajo pendiente, el pipeline duerme

Cuando no haya notas procesables en las carpetas de entrada de cada etapa, el loop no debe invocar IA innecesariamente; debe registrar estado y dormir hasta el siguiente ciclo. Esto reduce consumo inútil y ayuda a respetar cuotas. [file:21]

## Implementación

### CLI

Agregar soporte a la CLI para un modo loop explícito, por ejemplo:

- `pipeline run --loop`
- `pipeline run --loop --max-cycles 10`
- `pipeline run --loop --until-empty`
- `pipeline run --loop --dry-run`

La opción exacta puede resolverse en implementación, pero el principio es que el modo continuo sea explícito y compatible con el flujo actual de ejecución única. [file:21]

### Configuración runtime

Extender `runtime` en `pipeline.yaml` con campos nuevos para control fino del loop. La propuesta mínima es:

```yaml
runtime:
  delay_between_calls_ms: 3000
  delay_between_steps_ms: 8000
  max_retries: 4
  retry_backoff_seconds: 20
  switch_api_key_on_rate_limit: true
  dry_run: false

  loop_enabled: false
  loop_interval_seconds: 300
  idle_interval_seconds: 300
  error_cooldown_seconds: 120
  max_cycles: null
```

Definición funcional:

- `loop_enabled`: flag de config para habilitar política de loop si la CLI lo solicita.
- `loop_interval_seconds`: pausa normal entre ciclos completos con actividad.
- `idle_interval_seconds`: pausa cuando no hubo trabajo procesable.
- `error_cooldown_seconds`: pausa extra cuando un ciclo termina con errores operativos recuperables.
- `max_cycles`: límite opcional para ejecuciones acotadas en pruebas o cron largos. [file:17]

Opcionalmente, en una iteración posterior se podrá evaluar separar retardos por tipo de llamada:

```yaml
runtime:
  delay_between_text_calls_ms: 3000
  delay_between_embedding_calls_ms: 3000
  delay_between_steps_ms: 8000
```

Pero para esta versión no es obligatorio si `delay_between_calls_ms` ya puede aplicarse homogéneamente. [file:17]

### Orquestador de ciclo

Crear una función orquestadora de alto nivel, por ejemplo `run_loop()`, responsable de:

1. Cargar configuración.
2. Ejecutar un ciclo completo del pipeline.
3. Medir si hubo trabajo procesado, si hubo errores y cuántas llamadas IA se hicieron.
4. Dormir según el resultado del ciclo.
5. Repetir hasta condición de salida. [file:21]

Contrato operativo del ciclo:

- Si hubo trabajo procesado y no hubo error fatal, esperar `loop_interval_seconds`.
- Si no hubo trabajo procesable, esperar `idle_interval_seconds`.
- Si hubo error recuperable, esperar `error_cooldown_seconds`.
- Si se alcanza `max_cycles`, salir limpiamente.
- Si llega `SIGINT` o `KeyboardInterrupt`, cerrar con mensaje y estado consistente. [file:21]

### Throttling entre llamadas IA

Toda llamada de texto o embeddings hecha por los agentes debe pasar por una capa común de ejecución que:

- Registre inicio y fin.
- Aplique retry/backoff.
- Espere `delay_between_calls_ms` al finalizar.
- Clasifique si el error fue rate limit, timeout o fallo no recuperable. [file:17]

Esto evita duplicar sleeps en cada agente y asegura una política uniforme para Bea, Isabela, David y Basilio. [file:21]

### Throttling entre etapas

Luego de completar una etapa que sí consumió IA o generó transición efectiva, el orquestador debe esperar `delay_between_steps_ms` antes de invocar la siguiente etapa. Esto desacopla picos de uso y hace el pipeline más predecible. [file:17]

### Retry y rate limit

Implementar política común:

- Reintentar hasta `max_retries`.
- Esperar `retry_backoff_seconds * intento`.
- Si el error corresponde a rate limit y `switch_api_key_on_rate_limit` es `true`, alternar a la key secundaria cuando aplique en el proveedor soportado.
- Registrar el evento con severidad adecuada y continuar sin romper el estado del pipeline cuando el error sea recuperable. [file:17]

### Detección de trabajo disponible

Cada ciclo debe inspeccionar las carpetas de entrada de las etapas activas:

1. `propuestas`
2. `temas`
3. `en_redaccion`
4. `en_edicion` [file:21]

El pipeline solo debe invocar agentes sobre notas que cumplan las precondiciones de stage/frontmatter válidas. Si una etapa no tiene trabajo, se omite sin penalizar el resto del ciclo. [file:21]

### Logging y observabilidad mínima

Agregar logging por ciclo con datos como:

- número de ciclo
- timestamp de inicio y fin
- notas evaluadas
- notas movidas por etapa
- llamadas IA ejecutadas
- retries disparados
- rate limits detectados
- tiempo total dormido por throttling [file:17][file:21]

Esto permite ajustar la configuración conservadora con evidencia operativa y no por intuición.

### Compatibilidad

El cambio debe mantener:

- frontmatter como fuente de verdad del estado
- movimiento de archivos por etapa
- reglas/prompt fuera de código, en `rules/`
- Python como dueño del flujo y validación [file:21][file:24]

No debe introducir prompts hardcodeados ni lógica autónoma escondida en los agentes. [file:24]

## Validación

### Validación funcional

- Ejecutar el pipeline en modo actual de una sola pasada y confirmar que el comportamiento previo no cambia cuando `--loop` no está activo. [file:21]
- Ejecutar `pipeline run --loop` en un entorno con contenido de prueba y verificar que repite ciclos hasta interrupción o límite configurado.
- Verificar que un ciclo sin trabajo duerme `idle_interval_seconds` y no invoca IA.
- Verificar que un ciclo con trabajo aplica retardos entre llamadas y entre etapas según config. [file:17]

### Validación de resiliencia

- Simular error transitorio de proveedor y confirmar retries con backoff progresivo.
- Simular rate limit y confirmar uso de `switch_api_key_on_rate_limit` cuando haya key secundaria configurada. [file:17]
- Interrumpir con `Ctrl+C` durante sleep y durante procesamiento para verificar salida limpia sin corrupción de estado. [file:21]

### Validación de trazabilidad

- Confirmar que el loop registra por logs cada ciclo y su resultado.
- Confirmar que no se altera el contrato de stage/frontmatter.
- Confirmar que no se introducen prompts operativos hardcodeados. [file:21][file:24]

### Validación de documentación

Al cerrar implementación, actualizar obligatoriamente:

- `CHANGELOG.md`
- `SYSTEM_STATE.md`
- `VERSIONING.md`
- versión en `pyproject.toml` si se implementa el cambio completo como feature [file:24][file:20][file:19]

## Impacto en versión

Este cambio es una **feature** compatible, por lo que la versión objetivo pasa de `0.1.0` a `0.2.0`. [file:20]

## Commit convencional sugerido

`feat(runtime): agregar modo loop con throttling conservador configurable`

## Estado de tareas

- [x] diseñar
- [x] implementar
- [x] validar
- [x] documentar
- [x] actualizar versión