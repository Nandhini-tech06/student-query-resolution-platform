import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_student, get_current_user
from app.models.user import User
from app.models.query import StudentQuery

from app.schemas.query import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedKnowledgeItem,
    QueryAskRequest,
    QueryResponse,
    QueryFeedbackRequest,
    QueryHistoryItem,
    SourceCitation,
)

from app.services.rag.retriever import KnowledgeRetriever
from app.services.agent.query_agent import StudentQueryAgent
from app.services.llm.factory import get_llm_provider
from app.core.config import settings


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    prefix="/queries",
    tags=["Student Queries & Retrieval"],
)


# ================================================================
# RETRIEVE RELEVANT KNOWLEDGE
# ================================================================

@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
)
def retrieve_relevant_knowledge(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Core RAG Retrieval Service.

    Accepts a student's natural-language question,
    performs relevance scoring against active knowledge
    entries, and returns the most relevant institutional
    knowledge.

    This endpoint does NOT invoke Generative AI.
    """

    retriever = KnowledgeRetriever(db)

    retrieval_res = retriever.retrieve(
        query=request.question,
        category_hint=request.category,
        top_k=settings.RAG_TOP_K,
    )

    entries: List[RetrievedKnowledgeItem] = []

    for item, score in retrieval_res.items_with_scores:
        entries.append(
            RetrievedKnowledgeItem(
                id=item.id,
                title=item.title,
                content=item.content,
                category=item.category,
                source=item.source,
                source_url=item.source_url,
                tags=item.tags,
                relevance_score=score,
                updated_at=item.updated_at,
            )
        )

    return RetrievalResponse(
        question=request.question,
        category=request.category,
        is_confident=retrieval_res.is_confident,
        top_score=retrieval_res.top_score,
        results_count=len(entries),
        knowledge_entries=entries,
    )


# ================================================================
# ASK STUDENT QUERY
# ================================================================

@router.post(
    "/ask",
    response_model=QueryResponse,
)
def ask_student_query(
    request: QueryAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    AI Agent based student query-resolution endpoint.

    Workflow:

        Student Question
                ↓
        StudentQueryAgent
                ↓
        Intent Decision
                ↓
        RAG Retrieval
                ↓
        Confidence Check
                ↓
        Generative AI / Gemini
                ↓
        Grounded Answer
                ↓
        Source Citation
                ↓
        Save Query History
    """

    # ------------------------------------------------------------
    # Create the AI Agent
    # ------------------------------------------------------------

    agent = StudentQueryAgent(db)

    # ------------------------------------------------------------
    # Execute the complete agent workflow
    # ------------------------------------------------------------

    agent_result = agent.run(
        question=request.question,
        category_hint=request.category,
    )

    # ------------------------------------------------------------
    # Build source citations
    # ------------------------------------------------------------

    citations: List[SourceCitation] = []

    if agent_result.is_resolved:

        for source in agent_result.sources:

            # ----------------------------------------------------
            # Source returned as a string
            # Example:
            # "Library Working Hours (College Administration)"
            # ----------------------------------------------------

            if isinstance(source, str):

                citations.append(
                    SourceCitation(
                        title=source,
                        source_name="Institutional Knowledge Base",
                        source_url=None,
                        category=request.category,
                    )
                )

            # ----------------------------------------------------
            # Source returned as a dictionary
            # ----------------------------------------------------

            elif isinstance(source, dict):

                citations.append(
                    SourceCitation(
                        title=source.get(
                            "title",
                            "Institutional Knowledge",
                        ),
                        source_name=source.get(
                            "source_name",
                            "Institutional Knowledge Base",
                        ),
                        source_url=source.get(
                            "source_url"
                        ),
                        category=source.get(
                            "category",
                            request.category,
                        ),
                    )
                )

    # ------------------------------------------------------------
    # Save query to database
    # ------------------------------------------------------------

    new_query = StudentQuery(
        student_id=current_user.id,
        question=request.question,
        answer=agent_result.answer,
        category=request.category,
        sources_cited=json.dumps(
            [
                citation.model_dump()
                for citation in citations
            ]
        ),
        is_resolved=agent_result.is_resolved,
    )

    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    # ------------------------------------------------------------
    # Return response
    # ------------------------------------------------------------

    return QueryResponse(
        id=new_query.id,
        question=new_query.question,
        answer=new_query.answer,
        category=new_query.category,
        sources=citations,
        is_resolved=new_query.is_resolved,
        confidence_score=agent_result.confidence_score,
        created_at=new_query.created_at,
        agent_action=agent_result.agent_action,
        model_name=agent_result.model_name,
    )


# ================================================================
# QUERY HISTORY
# ================================================================

@router.get(
    "/history",
    response_model=List[QueryHistoryItem],
)
def get_student_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Retrieves the authenticated student's personal
    query history.
    """

    queries = (
        db.query(StudentQuery)
        .filter(
            StudentQuery.student_id == current_user.id
        )
        .order_by(
            StudentQuery.created_at.desc()
        )
        .limit(50)
        .all()
    )

    result = []

    for query_obj in queries:

        # --------------------------------------------------------
        # Convert stored JSON sources back to SourceCitation
        # --------------------------------------------------------

        try:

            sources_data = (
                json.loads(query_obj.sources_cited)
                if query_obj.sources_cited
                else []
            )

            citations = [
                SourceCitation(**item)
                for item in sources_data
            ]

        except Exception:

            citations = []

        # --------------------------------------------------------
        # Build history response
        # --------------------------------------------------------

        result.append(
            QueryHistoryItem(
                id=query_obj.id,
                question=query_obj.question,
                answer=query_obj.answer,
                category=query_obj.category,
                sources=citations,
                is_resolved=query_obj.is_resolved,
                feedback_rating=query_obj.feedback_rating,
                feedback_comment=query_obj.feedback_comment,
                created_at=query_obj.created_at,
            )
        )

    return result


# ================================================================
# SUBMIT QUERY FEEDBACK
# ================================================================

@router.post(
    "/{query_id}/feedback",
)
def submit_query_feedback(
    query_id: int,
    feedback: QueryFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Allows a student to provide feedback on their query.

    Supported ratings:

        HELPFUL
        UNHELPFUL
    """

    # ------------------------------------------------------------
    # Find query
    # ------------------------------------------------------------

    query_obj = (
        db.query(StudentQuery)
        .filter(
            StudentQuery.id == query_id
        )
        .first()
    )

    if not query_obj:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query record not found",
        )

    # ------------------------------------------------------------
    # Security check
    # ------------------------------------------------------------

    if query_obj.student_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to other student's query forbidden",
        )

    # ------------------------------------------------------------
    # Save feedback
    # ------------------------------------------------------------

    query_obj.feedback_rating = feedback.rating
    query_obj.feedback_comment = feedback.comment

    db.commit()

    return {
        "message": "Feedback recorded successfully",
        "rating": feedback.rating,
    }