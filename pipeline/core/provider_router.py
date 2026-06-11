from pipeline.core.config import AppConfig
from pipeline.core.http_clients import OllamaClient, OpenRouterClient


class ProviderRouter:
    def __init__(self, config: AppConfig):
        self.config = config

    def _resolve_ollama_base_url(self) -> str:
        target = self.config.providers.ollama.target
        if target == "cloud":
            return self.config.providers.ollama.cloud_url
        if target == "localhost":
            return self.config.providers.ollama.localhost_url
        if target == "lan":
            return self.config.providers.ollama.lan_url
        raise ValueError(f"Unknown ollama target: {target}")

    def describe_text_endpoint(self) -> str:
        provider = self.config.providers.active_text
        if provider == "ollama":
            return self._resolve_ollama_base_url()
        if provider == "openrouter":
            return self.config.providers.openrouter.base_url
        raise ValueError(f"Unknown text provider: {provider}")

    def describe_embeddings_endpoint(self) -> str:
        provider = self.config.providers.active_embeddings
        if provider == "ollama":
            return self._resolve_ollama_base_url()
        if provider == "openrouter":
            return self.config.providers.openrouter.base_url
        raise ValueError(f"Unknown embeddings provider: {provider}")

    def embeddings_client(self):
        provider = self.config.providers.active_embeddings
        if provider == "ollama":
            return OllamaClient(self.config)
        if provider == "openrouter":
            return OpenRouterClient(self.config)
        raise ValueError(f"Unknown embeddings provider: {provider}")

    def text_client(self):
        provider = self.config.providers.active_text
        if provider == "ollama":
            return OllamaClient(self.config)
        if provider == "openrouter":
            return OpenRouterClient(self.config)
        raise ValueError(f"Unknown text provider: {provider}")
