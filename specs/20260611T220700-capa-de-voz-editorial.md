# Spec: Capa de voz editorial y validación repetible

## Fecha
2026-06-11 22:07 -05

## Estado de tareas
- [x] Levantar material representativo del autor
- [x] Identificar rasgos estables de voz y tono
- [x] Definir reglas de prioridad entre cercanía y contundencia
- [x] Definir límites de uso de emojis
- [x] Definir frases firma permitidas por contexto
- [x] Definir despedidas permitidas
- [x] Definir frases prohibidas o de baja prioridad
- [x] Definir formalidad por tipo de publicación
- [x] Diseñar matriz por etapa
- [x] Diseñar protocolo de validación para LLM
- [x] Diseñar protocolo de validación para humano
- [ ] Implementar `rules/shared/author_voice.md`
- [ ] Actualizar `rules/shared/style.md`
- [ ] Actualizar `rules/shared/draft_style.md`
- [ ] Actualizar `rules/shared/editing_style.md`
- [ ] Añadir checklist formal de revisión humana
- [ ] Actualizar `docs/CHANGELOG.md`
- [ ] Actualizar `docs/SYSTEM_STATE.md`
- [ ] Actualizar `docs/VERSIONING.md`

## Objetivo
Incorporar una capa de voz editorial explícita, reusable y verificable para que el pipeline produzca borradores y ediciones alineados con la firma verbal de Raymundo Ycaza, sin depender de interpretaciones implícitas ni de prompts hardcodeados.

## Alcance
Esta spec cubre:

- La definición normativa de la voz editorial.
- La separación entre reglas generales de calidad y reglas de voz de autor.
- La modulación de la voz por etapa del pipeline.
- La clasificación de formalidad por tipo de publicación.
- El uso permitido de frases firma, despedidas y emojis.
- El protocolo de validación repetible para LLM y para revisión humana.

## No alcance
Esta spec no cubre:

- La publicación automática de contenidos.
- La reestructuración de etapas del pipeline.
- La incorporación de nuevos agentes.
- Un sistema de scoring automático por embeddings para estilo.
- Un clasificador ML de tono o formalidad.

## Contexto
El estado actual del proyecto establece que Python controla el flujo, que las reglas deben vivir en `rules/` y que ninguna salida debe depender de prompts hardcodeados [file:30]. También existen reglas compartidas genéricas para estilo, borrador y edición, pero todavía no expresan la firma verbal del autor ni un protocolo formal de validación de voz [file:10][file:11][file:12].

El análisis lingüístico disponible muestra una voz centrada en cercanía pedagógica, pragmatismo, contraste entre fricción y fluidez, explicación accesible de tecnología y cierre orientado a acción, pero varias de sus recomendaciones deben ajustarse a las decisiones editoriales más recientes del autor, especialmente en uso de emojis, cierres y formalidad [file:31].

## Problema
El pipeline puede producir textos útiles y coherentes, pero todavía no cuenta con una capa explícita de voz capaz de:

- preservar una identidad autoral consistente;
- distinguir entre cercanía y contundencia según intención;
- evitar frases que el autor rechaza;
- controlar el uso de emojis y despedidas;
- validar salidas con un criterio repetible y no puramente subjetivo.

Sin esta capa, el sistema corre el riesgo de sonar genérico, exageradamente marketero o incoherente entre etapas.

## Decisiones

### 1. Separación de responsabilidades
La voz editorial no debe incrustarse en `style.md` como bloque único. Se crea una separación clara:

- `rules/shared/style.md`: reglas base universales, claridad, utilidad, jerarquía y no redundancia [file:10].
- `rules/shared/author_voice.md`: firma verbal, prioridades de tono, frases permitidas, frases prohibidas, despedidas, formalidad y validación.
- `rules/shared/draft_style.md`: intensidad de voz para borrador [file:12].
- `rules/shared/editing_style.md`: intensidad de voz para edición [file:11].

### 2. Prioridad entre cercanía y contundencia
La voz no es lineal; depende de la intención editorial:

- Si la intención principal es conectar, acompañar o reducir fricción emocional, la cercanía tiene prioridad sobre la contundencia.
- Si la intención principal es aclarar un tema complejo, corregir confusión o fijar una idea crítica, la contundencia tiene prioridad sobre la cercanía.
- En cualquier caso, la contundencia no debe convertirse en dureza institucional y la cercanía no debe convertirse en tono infantil o excesivamente efusivo.

### 3. Política de emojis
Se define una política restrictiva de uso de emojis:

- Máximo 1 emoji por párrafo.
- Máximo 3 emojis por publicación.
- Uso solo en cierres y en ocasiones muy puntuales donde una frase exija una broma ligera, una ironía suave o un deseo utópico.
- No usar emojis como muletilla decorativa ni como marcador de escaneo por defecto.
- En piezas formales, el uso de emojis debe ser nulo o excepcional.

### 4. Frases firma permitidas por contexto
Se incorporará un bloque normativo llamado `Frases firma permitidas por contexto`.

#### Tecnología / formato largo
- "Recuerda que la tecnología..."
- "La automatización, bien utilizada, te ayudará a ser mejor en lo que haces."
- "Recuerda: no esperes más, aplica hoy mismo lo que has aprendido."

#### Reglas de uso
- "Recuerda que la tecnología..." solo se usa en publicaciones sobre tecnología y únicamente en formatos largos.
- "La automatización, bien utilizada, te ayudará a ser mejor en lo que haces." puede usarse como epígrafe, cierre o puente de valor en piezas de automatización.
- "Recuerda: no esperes más, aplica hoy mismo lo que has aprendido." se reserva exclusivamente para piezas de tipo tutorial o guía.
- Las frases firma no deben acumularse en un mismo cierre si eso perjudica naturalidad o ritmo.

### 5. Despedidas permitidas
Se incorporará un bloque normativo llamado `Despedidas permitidas`.

#### Despedidas válidas
- "Nos vemos"
- "Hasta una próxima ocasión"
- "Te veo en la siguiente"

#### Reglas de uso
- La despedida debe ir al final de la pieza, como remate último.
- "Nos vemos" es la despedida preferida en piezas no formales.
- En piezas formales, no debe usarse "Nos vemos".
- Solo debe aparecer una despedida por pieza.

### 6. Frases prohibidas o de baja prioridad
Se incorporará un bloque normativo llamado `Frases prohibidas o de baja prioridad`.

#### Prohibidas
- "Hola amigos"
- "Esto lo cambia todo"
- "Te llevará al siguiente nivel"
- "Llevará a tu [X] al siguiente nivel"
- "[X] mató a [Y]" en sentido de productos disruptivos
- Diminutivos innecesarios
- Frases genéricas de youtubers, blogueros o twitteros usadas solo para enganchar

#### De baja prioridad
- Fórmulas vacías que reemplacen ideas concretas por entusiasmo genérico.
- Frases de moda que no aporten precisión, contexto ni utilidad.
- Giros exageradamente promocionales que rompan la voz de mentor pragmático.

### 7. Formalidad por tipo de publicación
La formalidad deja de ser implícita y pasa a resolverse por taxonomía editorial.

| Tipo de publicación | Formalidad | Cercanía | Contundencia | Despedida | Emojis | Frase firma técnica |
|---|---|---|---|---|---|---|
| Tutorial técnico largo | Media | Alta | Media | Sí | Muy pocos | Sí |
| Guía técnica compleja | Alta | Media-baja | Alta | No | Ninguno o casi ninguno | Sí |
| Post educativo largo | Media | Alta | Media | Sí | Muy pocos | Solo si aplica |
| Artículo de análisis o reflexión | Media-alta | Media | Media-alta | Solo si no rompe el tono | Casi ninguno | Solo si encaja |
| Pieza institucional o formal | Alta | Baja | Alta | No | No | No |
| Publicación breve de red | Baja-media | Alta | Baja-media | Sí | Muy pocos | No |

#### Reglas derivadas
- Si una pieza es formal o institucional, no debe cerrar con "Nos vemos".
- Si una pieza es breve, no debe cargar frases firma largas.
- Si una pieza es tecnológica y larga, puede activar la frase firma técnica según pertinencia.

### 8. Matriz por etapa
La voz debe modularse por etapa, no repetirse con la misma intensidad.

| Archivo | Rol | Cercanía | Contundencia | Libertad expresiva | Frases firma | Emojis |
|---|---|---|---|---|---|---|
| `style.md` | Marco general | Neutra | Neutra | Baja | No define | No define |
| `draft_style.md` | Borrador | Alta | Media | Media-alta | Permitidas si aportan | Muy restringidos |
| `editing_style.md` | Edición | Media | Alta | Baja | Solo si ya están justificadas | Casi nunca |

#### Regla de etapa
- `draft_style.md` debe favorecer naturalidad, continuidad, ritmo y apertura retórica sin perder claridad [file:12].
- `editing_style.md` debe compactar, depurar y conservar la firma sin inflarla, priorizando precisión y legibilidad [file:11].

### 9. Protocolo de validación repetible para LLM
Se creará un protocolo estable para que los agentes autoevalúen la salida antes de promoverla de etapa.

#### Paso 1. Clasificación previa
El agente debe identificar:
- tipo de publicación;
- nivel de formalidad;
- intención principal;
- longitud esperada;
- si el tema activa o no frases firma técnicas.

#### Paso 2. Aplicación de tono
El agente debe resolver:
- si manda cercanía o contundencia;
- si la despedida aplica;
- si una frase firma es pertinente o excesiva;
- si el texto está sonando natural y no plantillado.

#### Paso 3. Restricciones duras
El agente debe verificar:
- máximo 1 emoji por párrafo;
- máximo 3 emojis por publicación;
- ausencia de frases prohibidas;
- ausencia de diminutivos innecesarios;
- ausencia de slogans genéricos o frases de moda;
- no usar "Nos vemos" en piezas formales.

#### Paso 4. Revisión del cierre
El agente debe confirmar:
- coherencia entre cierre y formalidad;
- una sola despedida final;
- uso correcto de CTA si la pieza es tutorial o guía;
- no acumular varias firmas en un mismo remate salvo que el ritmo lo soporte claramente.

#### Paso 5. Decisión
La salida solo puede avanzar si cumple todos los puntos. Si falla uno, debe reescribirse antes de cambiar de etapa.

### 10. Protocolo de validación repetible para humano
Se creará un checklist formal para `revision_humana`.

#### Fase A. Voz
- ¿Suena al autor y no a una plantilla?
- ¿Se percibe mentoría cercana y pragmática?
- ¿La relación entre cercanía y contundencia está bien resuelta?

#### Fase B. Restricciones
- ¿Respeta el límite de emojis?
- ¿Evita frases prohibidas?
- ¿Evita diminutivos innecesarios?
- ¿Evita moda verbal prestada de internet?

#### Fase C. Cierre
- ¿La despedida es válida?
- ¿La pieza formal evita "Nos vemos"?
- ¿La pieza tutorial o guía puede usar la frase de acción si encaja?
- ¿La despedida aparece solo al final?

#### Fase D. Publicabilidad
- ¿El texto está claro?
- ¿El ritmo es natural?
- ¿La voz es consistente de inicio a fin?
- ¿Está listo para revisión final o publicación sin reescritura estructural?

## Implementación

### Archivos nuevos
- `rules/shared/author_voice.md`

### Archivos a modificar
- `rules/shared/style.md`
- `rules/shared/draft_style.md`
- `rules/shared/editing_style.md`
- `docs/CHANGELOG.md`
- `docs/SYSTEM_STATE.md`
- `docs/VERSIONING.md`

### Contenido mínimo de `author_voice.md`
El archivo debe incluir, al menos, las siguientes secciones:

1. Propósito de la voz.
2. Perfil general de tono.
3. Regla de prioridad entre cercanía y contundencia.
4. Política de emojis.
5. Frases firma permitidas por contexto.
6. Despedidas permitidas.
7. Frases prohibidas o de baja prioridad.
8. Formalidad por tipo de publicación.
9. Checklist LLM.
10. Checklist humano.
11. Ejemplos breves de uso correcto e incorrecto.

### Integración con etapas
- `David` debe leer `author_voice.md` junto con `draft_style.md` para producir borradores más cercanos a la firma del autor.
- `Basilio` debe leer `author_voice.md` junto con `editing_style.md` para depurar sin borrar personalidad.
- `Bea` e `Isabela` no necesitan heredar toda la expresividad de voz, pero sí deben conocer restricciones duras de tono cuando generen observaciones o estructuras.

## Validación

### Validación determinista mínima sugerida
Se recomienda añadir validaciones programáticas básicas para detectar:

- ocurrencia de frases prohibidas;
- conteo máximo de emojis;
- presencia de más de una despedida final;
- uso de "Nos vemos" en piezas marcadas como formales;
- uso de "Recuerda: no esperes más, aplica hoy mismo lo que has aprendido." en piezas que no sean tutorial o guía.

### Validación editorial
Se considerará aceptada la implementación cuando:

- exista `author_voice.md` bajo `rules/shared/`;
- `draft_style.md` y `editing_style.md` reflejen la matriz definida;
- la revisión humana tenga un checklist formal;
- al menos 3 casos de prueba muestren diferencias correctas entre pieza formal, tutorial técnico y post breve.

## Compatibilidad
La propuesta es compatible con la filosofía vigente del proyecto porque:

- mantiene prompts y reglas fuera del código [file:30];
- preserva el control determinista desde Python [file:30];
- usa frontmatter y etapas existentes sin romper contratos [file:30];
- no exige reemplazar agentes ni introducir dependencias externas.

## Riesgos
- Sobrecargar la voz con demasiadas frases firma puede volverla mecánica.
- Convertir la despedida en obligación ciega puede producir cierres forzados.
- Hacer demasiadas validaciones rígidas puede castigar textos correctos pero creativos.

## Mitigaciones
- Tratar las frases firma como recursos contextuales, no como obligación constante.
- Mantener solo restricciones duras donde exista una preferencia inequívoca del autor.
- Dejar espacio para criterio editorial humano en ritmo, naturalidad y cierre.

## Impacto en versionado
Este cambio modifica comportamiento editorial, reglas compartidas y validación del sistema. Corresponde un incremento **minor**.

### Versión resultante sugerida
`0.3.0`

## Conventional commit sugerido
`feat(voz): agregar capa editorial de voz de autor y validación repetible`

## Criterio de cierre de la spec
La spec se considera cerrada cuando el repositorio incluya la nueva capa normativa en `rules/shared/`, los archivos de estilo por etapa estén ajustados, la documentación de estado/versionado quede actualizada y exista un checklist formal reutilizable para revisión humana.
