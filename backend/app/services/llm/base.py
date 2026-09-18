from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from app.models.knowledge import KnowledgeItem


class LLMResult(BaseModel):
    text: str
    model_name: str
    provider_name: str
    is_grounded: bool = True
    sources_cited: List[str] = []


FALLBACK_UNAVAILABLE_MESSAGE = (
    "I could not find verified institutional records or approved policies regarding your question. "
    "To ensure you receive accurate and authorized information without speculation, please contact "
    "the relevant University Administrative Office or check the official student notices portal."
)


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_answer(self, query: str, retrieved_docs: List[KnowledgeItem]) -> LLMResult:
        """Generate a grounded answer based strictly on retrieved knowledge documents."""
        pass
