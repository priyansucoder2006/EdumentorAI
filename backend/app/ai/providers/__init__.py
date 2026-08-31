from app.ai.providers.base import BaseLLMProvider, BaseEmbeddingProvider
from app.ai.providers.mock_provider import MockPedagogicalProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.embedding_provider import get_embedding_provider, LocalEmbeddingProvider, OpenAIEmbeddingProvider
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini" and settings.LLM_API_KEY:
        return GeminiProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
    elif (provider == "openai" or provider == "groq") and settings.LLM_API_KEY:
        base_url = "https://api.groq.com/openai/v1" if provider == "groq" else "https://api.openai.com/v1"
        return OpenAIProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL, base_url=base_url)
    return MockPedagogicalProvider()


__all__ = [
    "BaseLLMProvider",
    "BaseEmbeddingProvider",
    "MockPedagogicalProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "LocalEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "get_llm_provider",
    "get_embedding_provider",
]
