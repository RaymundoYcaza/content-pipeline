# VERSIONING

## Versión actual objetivo
0.3.0

## Motivo del incremento
Este incremento corresponde a una nueva feature editorial:
- capa de voz de autor;
- reglas de formalidad por tipo de publicación;
- frases firma permitidas por contexto;
- despedidas permitidas;
- frases prohibidas o de baja prioridad;
- protocolos repetibles de validación para LLM y humano.

## Tipo de cambio
Minor.

## Criterio
Toda feature nueva incrementa la versión menor cuando no rompe compatibilidad del sistema.

## Estado
La versión objetivo ya está definida a nivel documental. La confirmación final de esta versión depende de las pruebas de validación de la nueva capa de voz.

## Próximo ajuste posible
Si las pruebas revelan un problema de comportamiento o una corrección menor de reglas, el siguiente cambio podría ser un patch sobre `0.3.0`. Si aparecen cambios estructurales no compatibles, se requerirá una revisión mayor.