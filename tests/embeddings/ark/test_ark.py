import json
import unittest

import httpx

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.ark import ArkEmbedding


class ArkEmbeddingTests(unittest.TestCase):
    def make_embedder(self, handler):
        config = BaseEmbedderConfig(
            api_key="unit-test-key",
            model="doubao-embedding-vision",
            embedding_dims=1024,
            openai_base_url="https://ark.test/api/coding/v3",
        )
        config.http_client = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(config.http_client.close)
        return ArkEmbedding(config)

    def test_default_http_client_created(self):
        embedder = ArkEmbedding(BaseEmbedderConfig(api_key="unit-test-key"))
        self.addCleanup(embedder.client.close)
        self.assertIsInstance(embedder.client, httpx.Client)

    def test_ark_request_and_vector(self):
        def handler(request):
            self.assertEqual(request.url.path, "/api/coding/v3/embeddings/multimodal")
            self.assertEqual(request.headers["authorization"], "Bearer unit-test-key")
            payload = json.loads(request.content)
            self.assertEqual(payload["input"], [{"type": "text", "text": "memory test"}])
            self.assertEqual(payload["dimensions"], 1024)
            return httpx.Response(200, json={"data": {"embedding": [0.25] * 1024}})

        self.assertEqual(self.make_embedder(handler).embed("memory test"), [0.25] * 1024)

    def test_wrong_dimensions_rejected(self):
        embedder = self.make_embedder(lambda request: httpx.Response(200, json={"data": {"embedding": [0.1]}}))
        with self.assertRaisesRegex(ValueError, "invalid embedding vector"):
            embedder.embed("test")

    def test_nonfinite_vector_rejected(self):
        response = {"data": {"embedding": [0.0] * 1023 + [float("nan")]}}
        embedder = self.make_embedder(lambda request: httpx.Response(200, content=json.dumps(response)))
        with self.assertRaisesRegex(ValueError, "invalid embedding vector"):
            embedder.embed("test")

    def test_auth_failure_propagates(self):
        embedder = self.make_embedder(lambda request: httpx.Response(401, json={"error": "invalid credential"}))
        with self.assertRaises(httpx.HTTPStatusError):
            embedder.embed("test")


if __name__ == "__main__":
    unittest.main()
