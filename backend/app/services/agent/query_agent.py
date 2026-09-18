from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.rag.retriever import KnowledgeRetriever
from app.services.llm.factory import get_llm_provider


class QueryAgentResult:
    """
    Structured result returned by the AI Query Agent.
    """

    def __init__(
        self,
        answer: str,
        sources: list,
        is_resolved: bool,
        confidence_score: float,
        agent_action: str,
        model_name: str,
    ):
        self.answer = answer
        self.sources = sources
        self.is_resolved = is_resolved
        self.confidence_score = confidence_score
        self.agent_action = agent_action
        self.model_name = model_name


class StudentQueryAgent:
    """
    AI Agent responsible for orchestrating student query resolution.

    The agent:
    1. Receives the student's question.
    2. Determines whether institutional knowledge is required.
    3. Uses the RAG retriever to search verified knowledge.
    4. Evaluates retrieval confidence.
    5. Calls the Generative AI provider when sufficient context exists.
    6. Prevents unsupported answers when reliable context is unavailable.
    """

    def __init__(self, db: Session):
        self.db = db
        self.retriever = KnowledgeRetriever(db)
        self.llm_provider = get_llm_provider()

    def _needs_institutional_knowledge(self, question: str) -> bool:
        """
        Determines whether the question is likely to require
        university/college-specific information.

        This is intentionally conservative because the system
        must avoid inventing institutional information.
        """

        institutional_keywords = {
            "college",
            "university",
            "campus",
            "library",
            "attendance",
            "exam",
            "examination",
            "semester",
            "course",
            "courses",
            "department",
            "fee",
            "fees",
            "admission",
            "admissions",
            "grading",
            "grade",
            "sgpa",
            "cgpa",
            "scholarship",
            "hostel",
            "academic",
            "academic year",
            "regulation",
            "regulations",
            "policy",
            "policies",
            "certificate",
            "placement",
            "placements",
        }

        question_lower = question.lower()

        return any(
            keyword in question_lower
            for keyword in institutional_keywords
        )

    def run(
        self,
        question: str,
        category_hint: Optional[str] = None,
    ) -> QueryAgentResult:

        question = question.strip()

        if not question:
            return QueryAgentResult(
                answer=(
                    "Please provide a valid question so I can "
                    "search the verified university records."
                ),
                sources=[],
                is_resolved=False,
                confidence_score=0.0,
                agent_action="REJECT_EMPTY_QUERY",
                model_name="none",
            )

        # ---------------------------------------------------------
        # AGENT DECISION 1
        # Determine whether institutional retrieval is appropriate.
        # ---------------------------------------------------------

        needs_knowledge = self._needs_institutional_knowledge(question)

        if not needs_knowledge:
            return QueryAgentResult(
                answer=(
                    "This query does not appear to require "
                    "institution-specific information. Please ask "
                    "a question related to the university's verified "
                    "academic, administrative, or campus records."
                ),
                sources=[],
                is_resolved=False,
                confidence_score=0.0,
                agent_action="REJECT_NON_INSTITUTIONAL_QUERY",
                model_name="none",
            )

        # ---------------------------------------------------------
        # AGENT ACTION 2
        # Retrieve verified institutional knowledge.
        # ---------------------------------------------------------

        retrieval_result = self.retriever.retrieve(
            query=question,
            category_hint=category_hint,
            top_k=settings.RAG_TOP_K,
        )

        # ---------------------------------------------------------
        # AGENT DECISION 2
        # Evaluate retrieval confidence.
        # ---------------------------------------------------------

        if not retrieval_result.is_confident:
            return QueryAgentResult(
                answer=(
                    "The specific information for this query is not "
                    "available in the current verified university "
                    "records. Please check with the respective "
                    "department office."
                ),
                sources=[],
                is_resolved=False,
                confidence_score=retrieval_result.top_score,
                agent_action="NO_CONFIDENT_KNOWLEDGE_FOUND",
                model_name="none",
            )

        # ---------------------------------------------------------
        # AGENT ACTION 3
        # Send retrieved institutional context to Generative AI.
        # ---------------------------------------------------------

        llm_result = self.llm_provider.generate_answer(
            query=question,
            retrieved_docs=retrieval_result.items,
        )

        # ---------------------------------------------------------
        # AGENT DECISION 3
        # Verify that the generated answer is grounded.
        # ---------------------------------------------------------

        is_resolved = (
            retrieval_result.is_confident
            and llm_result.is_grounded
        )

        if is_resolved:
            agent_action = "RETRIEVE_AND_GENERATE"
        else:
            agent_action = "GENERATION_NOT_GROUNDED"

        return QueryAgentResult(
            answer=llm_result.text,
            sources=llm_result.sources_cited,
            is_resolved=is_resolved,
            confidence_score=retrieval_result.top_score,
            agent_action=agent_action,
            model_name=llm_result.model_name,
        )