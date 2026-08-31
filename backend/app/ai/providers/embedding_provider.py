import math
import hashlib
from typing import List, Optional
import httpx
from app.ai.providers.base import BaseEmbeddingProvider
from app.core.config import settings
from app.core.logging import logger


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic dense semantic embedding provider.
    Uses multi-hash n-gram projection with normalization to provide 
    reproducible 384-dimensional dense vectors without requiring heavy PyTorch weights.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def _text_to_vector(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        clean_text = text.lower().strip()
        words = clean_text.split()
        if not words:
            return vec

        # Bag of words + character trigrams
        tokens = words + [clean_text[i:i+3] for i in range(max(0, len(clean_text)-2))]
        for token in tokens:
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h % self.dim
            weight = 1.0 + (h % 5) * 0.2
            vec[idx] += weight

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    async def embed_text(self, text: str) -> List[float]:
        return self._text_to_vector(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (norm1 * norm2)))


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.local_fallback = LocalEmbeddingProvider()

    async def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            return await self.local_fallback.embed_text(text)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"input": text, "model": self.model}
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["data"][0]["embedding"]
        except Exception as e:
            logger.warning(f"OpenAI embedding error, falling back to local: {e}")
        return await self.local_fallback.embed_text(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return await self.local_fallback.embed_documents(texts)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"input": texts, "model": self.model}
                )
                if res.status_code == 200:
                    data = res.json()
                    return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.warning(f"OpenAI batch embedding error: {e}")
        return await self.local_fallback.embed_documents(texts)

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        return self.local_fallback.similarity(vec1, vec2)


def get_embedding_provider() -> BaseEmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "openai" and settings.LLM_API_KEY:
        return OpenAIEmbeddingProvider(api_key=settings.LLM_API_KEY)
    return LocalEmbeddingProvider(dim=settings.EMBEDDING_DIM)
