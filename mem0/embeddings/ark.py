"""Text embeddings through the Volcengine Ark multimodal endpoint."""

import math
import os

import httpx
from pydantic import TypeAdapter

from mem0.embeddings.base import EmbeddingBase


class ArkEmbedding(EmbeddingBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.client = self.config.http_client or httpx.Client()

    def embed(self, text, memory_action=None):
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Ark API key is required")
        base_url = self.config.openai_base_url or os.environ.get(
            "OPENAI_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
        )
        dimensions = self.config.embedding_dims or 1024
        response = self.client.post(
            base_url.rstrip("/") + "/embeddings/multimodal",
            headers={"Authorization": "Bearer " + api_key},
            json={
                "model": self.config.model or "doubao-embedding-vision",
                "input": [{"type": "text", "text": text}],
                "encoding_format": "float",
                "dimensions": dimensions,
            },
            timeout=30,
        )
        response.raise_for_status()
        vector = TypeAdapter(list[float]).validate_python(response.json()["data"]["embedding"], strict=True)
        if len(vector) != dimensions or not all(math.isfinite(value) for value in vector):
            raise ValueError("Ark returned an invalid embedding vector")
        return vector
