import os
from typing import Any
import requests

from pipeline.core.config import AppConfig
from pipeline.core.retry import retry_with_backoff


class OllamaClient:
    def __init__(self, config: AppConfig):
        self.config = config

    def _base_url(self) -> str:
        target = self.config.providers.ollama.target
        if target == "cloud":
            return self.config.providers.ollama.cloud_url.rstrip("/")
        if target == "localhost":
            return self.config.providers.ollama.localhost_url.rstrip("/")
        if target == "lan":
            return self.config.providers.ollama.lan_url.rstrip("/")
        raise ValueError(f"Unknown ollama target: {target}")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key_env = self.config.providers.ollama.api_key_env
        api_key = os.getenv(api_key_env, "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        payload = {
            "model": model or self.config.providers.ollama.embedding_model,
            "input": texts,
        }

        def _call():
            response = requests.post(
                f"{self._base_url()}/api/embed",
                json=payload,
                headers=self._headers(),
                timeout=120,
            )
            response.raise_for_status()
            return response.json()

        data = retry_with_backoff(
            _call,
            max_retries=self.config.runtime.max_retries,
            base_delay_seconds=self.config.runtime.retry_backoff_seconds,
        )
        if "embeddings" in data:
            return data["embeddings"]
        if "embedding" in data:
            return [data["embedding"]]
        raise ValueError(f"Unexpected Ollama embeddings response: {data}")

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        payload: dict[str, Any] = {
            "model": model or self.config.providers.ollama.text_model,
            "messages": messages,
            "stream": False,
        }

        def _call():
            response = requests.post(
                f"{self._base_url()}/api/chat",
                json=payload,
                headers=self._headers(),
                timeout=180,
            )
            response.raise_for_status()
            return response.json()

        data = retry_with_backoff(
            _call,
            max_retries=self.config.runtime.max_retries,
            base_delay_seconds=self.config.runtime.retry_backoff_seconds,
        )
        return data["message"]["content"]


class OpenRouterClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self._key_index = 0

    def _base_url(self) -> str:
        return self.config.providers.openrouter.base_url.rstrip("/")

    def _keys(self) -> list[str]:
        return [
            os.getenv(self.config.providers.openrouter.api_key_env_primary, ""),
            os.getenv(self.config.providers.openrouter.api_key_env_secondary, ""),
        ]

    def _api_key(self) -> str:
        keys = [k for k in self._keys() if k]
        if not keys:
            raise ValueError("Missing OpenRouter API key")
        return keys[min(self._key_index, len(keys) - 1)]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key()}",
            "Content-Type": "application/json",
        }

    def _rotate_key(self):
        self._key_index += 1

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        payload: dict[str, Any] = {
            "model": model or self.config.providers.openrouter.embedding_model,
            "input": texts,
        }

        def _call():
            response = requests.post(
                f"{self._base_url()}/embeddings",
                json=payload,
                headers=self._headers(),
                timeout=120,
            )
            if response.status_code == 429 and self.config.runtime.switch_api_key_on_rate_limit:
                self._rotate_key()
            response.raise_for_status()
            return response.json()

        data = retry_with_backoff(
            _call,
            max_retries=self.config.runtime.max_retries,
            base_delay_seconds=self.config.runtime.retry_backoff_seconds,
        )
        return [item["embedding"] for item in data.get("data", [])]

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        payload: dict[str, Any] = {
            "model": model or self.config.providers.openrouter.text_model,
            "messages": messages,
        }

        def _call():
            response = requests.post(
                f"{self._base_url()}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=180,
            )
            if response.status_code == 429 and self.config.runtime.switch_api_key_on_rate_limit:
                self._rotate_key()
            response.raise_for_status()
            return response.json()

        data = retry_with_backoff(
            _call,
            max_retries=self.config.runtime.max_retries,
            base_delay_seconds=self.config.runtime.retry_backoff_seconds,
        )
        return data["choices"][0]["message"]["content"]
