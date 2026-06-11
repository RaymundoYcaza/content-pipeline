from pathlib import Path
from pipeline.core.config import load_config
from pipeline.core.provider_router import ProviderRouter


def test_provider_router_resolves_ollama_cloud():
    cfg = load_config(Path("config/pipeline.yaml"))
    router = ProviderRouter(cfg)
    assert "ollama.com" in router.describe_text_endpoint()
