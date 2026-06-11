# Provider Routing Spec

## Goal
Permitir alternar entre Ollama y OpenRouter para texto y embeddings sin cambiar el código del pipeline.

## Requirements
- Selección independiente para text y embeddings.
- Soporte para Ollama cloud, localhost y host LAN.
- Soporte para API key primaria/secundaria en OpenRouter.
- Punto central de configuración en `config/pipeline.yaml`.
