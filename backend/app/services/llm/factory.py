import os

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider, FALLBACK_UNAVAILABLE_MESSAGE
from app.services.llm.direct import DirectGroundingProvider
from app.services.llm.gemini import GeminiLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    api_key = (
        settings.GEMINI_API_KEY
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )

    if api_key and api_key.strip():
        return GeminiLLMProvider(
            api_key=api_key.strip(),
            model_name=settings.GEMINI_MODEL,
        )

    return DirectGroundingProvider()


__all__ = [
    "get_llm_provider",
    "FALLBACK_UNAVAILABLE_MESSAGE",
    "BaseLLMProvider",
]