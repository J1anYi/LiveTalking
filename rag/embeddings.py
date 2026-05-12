"""DashScope Embedding API client.

Uses OpenAI-compatible mode to call DashScope Embedding API.

Verification results:
    - Model: text-embedding-v3
    - Dimensions: 1024
"""

import os
from openai import OpenAI


class DashScopeEmbedding:
    """DashScope Embedding API client.

    Uses OpenAI-compatible mode to call DashScope Embedding API.

    Verification results:
        - Model: text-embedding-v3
        - Dimensions: 1024
    """

    def __init__(
        self,
        model: str = "text-embedding-v3",
        api_key: str | None = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout: float = 30.0,
    ) -> None:
        """Initialize Embedding client.

        Args:
            model: Embedding model name, default text-embedding-v3
            api_key: DashScope API Key, default from DASHSCOPE_API_KEY env var
            base_url: API base URL
            timeout: Request timeout in seconds

        Raises:
            ValueError: If api_key not provided and env var not set
        """
        self._model = model
        self._timeout = timeout

        if api_key is None:
            api_key = os.environ.get("DASHSCOPE_API_KEY")
            if api_key is None:
                raise ValueError(
                    "DASHSCOPE_API_KEY not set. "
                    "Please set the environment variable or pass api_key parameter."
                )

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of texts, max 20 texts

        Returns:
            List of embedding vectors, each with 1024 floats

        Raises:
            ValueError: If texts is empty or has more than 20 items
            RuntimeError: If API call fails
        """
        if not texts:
            raise ValueError("texts cannot be empty")
        if len(texts) > 20:
            raise ValueError("texts cannot have more than 20 items")

        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(f"Embedding API call failed: {e}") from e

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query.

        Args:
            query: Query text

        Returns:
            Query embedding vector with 1024 floats
        """
        return self.embed([query])[0]

    @property
    def dimensions(self) -> int:
        """Return embedding dimensions."""
        return 1024

    @property
    def model(self) -> str:
        """Return model name."""
        return self._model
