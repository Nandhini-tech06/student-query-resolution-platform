from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ================================================================
# RETRIEVAL REQUEST
# ================================================================

class RetrievalRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000
    )

    category: Optional[str] = Field(
        None,
        max_length=100
    )


# ================================================================
# RETRIEVED KNOWLEDGE ITEM
# ================================================================

class RetrievedKnowledgeItem(BaseModel):
    id: int
    title: str
    content: str
    category: str
    source: str
    source_url: Optional[str] = None
    tags: Optional[str] = None
    relevance_score: float
    updated_at: datetime


# ================================================================
# RETRIEVAL RESPONSE
# ================================================================

class RetrievalResponse(BaseModel):
    question: str
    category: Optional[str] = None

    is_confident: bool
    top_score: float
    results_count: int

    knowledge_entries: List[RetrievedKnowledgeItem] = []


# ================================================================
# QUERY ASK REQUEST
# ================================================================

class QueryAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000
    )

    category: Optional[str] = Field(
        None,
        max_length=100
    )


# ================================================================
# SOURCE CITATION
# ================================================================

class SourceCitation(BaseModel):
    title: str
    source_name: str
    source_url: Optional[str] = None
    category: Optional[str] = None


# ================================================================
# QUERY RESPONSE
# ================================================================

class QueryResponse(BaseModel):
    id: int

    question: str

    answer: str

    category: Optional[str] = None

    sources: List[SourceCitation] = []

    is_resolved: bool

    confidence_score: float = 0.0

    created_at: datetime

    # ============================================================
    # AI AGENT INFORMATION
    # ============================================================

    # Shows what action the StudentQueryAgent performed.
    #
    # Examples:
    # RETRIEVE_AND_GENERATE
    # NO_CONFIDENT_KNOWLEDGE_FOUND
    # REJECT_NON_INSTITUTIONAL_QUERY
    # REJECT_EMPTY_QUERY
    # GENERATION_NOT_GROUNDED
    #
    agent_action: str = "UNKNOWN"

    # Shows which LLM/model generated the answer.
    #
    # Example:
    # gemini-2.5-flash
    #
    model_name: str = "unknown"


# ================================================================
# QUERY FEEDBACK REQUEST
# ================================================================

class QueryFeedbackRequest(BaseModel):
    rating: str = Field(
        ...,
        pattern="^(HELPFUL|UNHELPFUL)$"
    )

    comment: Optional[str] = Field(
        None,
        max_length=500
    )


# ================================================================
# QUERY HISTORY ITEM
# ================================================================

class QueryHistoryItem(BaseModel):
    id: int

    question: str

    answer: str

    category: Optional[str] = None

    sources: List[SourceCitation] = []

    is_resolved: bool

    feedback_rating: Optional[str] = None

    feedback_comment: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True