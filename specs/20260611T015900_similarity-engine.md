# Similarity Engine Spec

## Objective
Calcular similitud semántica entre propuestas nuevas y contenido existente usando embeddings vía API.

## Rules
- Python calcula cosine similarity.
- El proveedor de embeddings es configurable.
- Se retorna score máximo contra el corpus existente.
- Se clasifica en approve, review o reject según thresholds configurables.
