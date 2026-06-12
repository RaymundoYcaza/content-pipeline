# `20260612T110700editorial-depth-hook-control.md`

## Objetivo

Controlar de forma determinista la **longitud**, **detalle**, **profundidad** y **tipo de apertura** de las piezas editoriales generadas por el pipeline, evitando arranques genéricos como “Bienvenido a...” y obligando a una apertura con gancho contextual para la audiencia. 

## Contexto

El pipeline editorial actual ya opera con frontmatter como fuente de verdad, movimiento de archivos por etapa y reglas externas a la implementación, por lo que este cambio debe integrarse como una extensión de las reglas editoriales, no como lógica hardcodeada en el prompt operativo. 
La salida de texto debe seguir siendo validable por Python, para que la orquestación conserve trazabilidad y no dependa de la subjetividad del modelo. 

## Alcance

Este cambio aplica a la etapa de redacción editorial y a cualquier agente que produzca el texto final de una pieza.  
La spec define dos controles principales: un **perfil de profundidad** y una **política de apertura**.  
También define criterios de validación para rechazar salidas demasiado genéricas, demasiado superficiales o con introducciones no permitidas. 

## Reglas de profundidad

La pieza debe poder declararse con un perfil de profundidad explícito en la spec o en el frontmatter de la nota.  
Se admiten, como mínimo, estos perfiles:

- `shallow`: enfoque breve, una idea central, desarrollo ligero.
- `medium`: desarrollo equilibrado, contexto + explicación + ejemplo.
- `deep`: cobertura amplia, matices, ejemplos, implicaciones y cierre más elaborado.

Cada perfil debe mapearse a expectativas observables, por ejemplo:

- Rango de extensión objetivo.
- Número mínimo y máximo de secciones.
- Presencia obligatoria de ejemplo, caso o aplicación.
- Nivel de contextualización exigido.
- Profundidad mínima de análisis o explicación. 

La spec debe permitir que Python valide la salida contra esas expectativas sin pedirle al modelo que “escriba más” de forma vaga. 

## Política de apertura

La primera frase o el primer bloque del texto no debe comenzar con saludos genéricos, introducciones vacías ni metadiscurso editorial.  
Quedan desaconsejadas o prohibidas fórmulas como:

- “Bienvenido a...”
- “En este artículo...”
- “Hoy vamos a hablar de...”
- “A continuación...”
- “En el mundo actual...”

La apertura debe arrancar con un gancho contextual que conecte con una situación real de la audiencia, por ejemplo:

- una fricción recurrente,
- una escena reconocible,
- una pregunta incómoda,
- una expectativa concreta,
- una consecuencia práctica. 

La validación debe aceptar inicios como:

- “Seguramente ya te has encontrado con...”
- “Imagina que estás...”
- “Si estás empezando con...”
- “Te pasa esto cuando...”
- “El problema aparece justo cuando...”  

Estos patrones son ejemplos permitidos, no plantillas obligatorias. 

## Reglas de validación

La salida editorial debe considerarse inválida si ocurre cualquiera de estas condiciones:

- La apertura comienza con una bienvenida genérica o frase vacía.
- La introducción no contiene un problema, escena o contexto útil para la audiencia.
- La pieza no alcanza el perfil de profundidad solicitado.
- El texto incluye relleno que no aporta contexto, claridad o progreso argumental.
- La extensión final queda fuera del rango definido para el perfil elegido. 

La validación debe ser determinista y ejecutarse en Python antes de aceptar la nota como válida.  
Si la salida falla, la nota no debe avanzar de etapa hasta corregirse. 

## Contrato de configuración

La spec debe admitir una configuración editorial mínima, ya sea en frontmatter o en rules, con campos como estos:

- `depth_profile`
- `target_length`
- `min_sections`
- `max_sections`
- `opening_policy`
- `opening_blacklist`
- `opening_hook_requirements`

La idea es que el sistema pueda ajustar el estilo sin tocar el flujo central ni introducir prompts operativos hardcodeados. 

## Implementación esperada

Python debe leer la configuración editorial y validar la respuesta generada.  
El agente de redacción debe recibir reglas claras sobre profundidad y apertura desde `rules/`, no desde texto fijo incrustado en código.  
El flujo debe continuar siendo determinista: si el texto no cumple, se rechaza; si cumple, avanza. 

## Criterios de aceptación

- La pieza puede generarse en distintos niveles de profundidad.
- La primera frase no usa saludos genéricos ni aperturas vacías.
- La introducción arranca con un gancho contextual reconocible.
- La validación rechaza aperturas genéricas.
- La validación rechaza piezas demasiado breves o demasiado superficiales para el perfil.
- El comportamiento queda documentado en changelog, estado y versionado. 

## No alcance

Este cambio no redefine la arquitectura del pipeline.  
No introduce paralelismo, no cambia el sistema de frontmatter como fuente de verdad, no mueve reglas al código y no altera el loop ni el throttling operativo existente. 
Tampoco fija una plantilla rígida de intros; solo define restricciones y criterios de calidad. 

## Estado de tareas

- [ ] Crear archivo de spec con timestamp.
- [ ] Actualizar reglas editoriales en `rules/`.
- [ ] Implementar validación determinista en Python.
- [ ] Ajustar frontmatter o config si hace falta.
- [ ] Actualizar `CHANGELOG.md`.
- [ ] Actualizar `SYSTEM_STATE.md`.
- [ ] Actualizar `VERSIONING.md`.
- [ ] Verificar ejemplos de apertura aceptable y rechazada.

## Commit convencional sugerido

`feat(editorial): controlar profundidad y gancho de apertura`

## Versión resultante

`0.3.0`  