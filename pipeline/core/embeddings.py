from pipeline.core.provider_router import ProviderRouter
from pipeline.core.config import AppConfig


class EmbeddingService:
    def __init__(self, config: AppConfig):
        self.router = ProviderRouter(config)

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self.router.embeddings_client()
        return client.embed(texts)
