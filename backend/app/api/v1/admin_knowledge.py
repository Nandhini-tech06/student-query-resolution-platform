from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.knowledge import KnowledgeItem
from app.models.query import StudentQuery
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse

router = APIRouter(prefix="/admin", tags=["Admin Knowledge Management"])


@router.get("/knowledge", response_model=List[KnowledgeResponse])
def list_knowledge_items(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Lists knowledge base documents with optional filtering (Admin Only)."""
    query = db.query(KnowledgeItem)

    if category:
        query = query.filter(KnowledgeItem.category == category)
    if is_active is not None:
        query = query.filter(KnowledgeItem.is_active == is_active)
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            (KnowledgeItem.title.ilike(search_pattern)) |
            (KnowledgeItem.content.ilike(search_pattern)) |
            (KnowledgeItem.source.ilike(search_pattern))
        )

    return query.order_by(KnowledgeItem.updated_at.desc()).offset(skip).limit(limit).all()


@router.post("/knowledge", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_item(
    item_in: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Adds a new institutional document or policy to the knowledge base (Admin Only)."""
    new_item = KnowledgeItem(
        title=item_in.title,
        category=item_in.category.lower().strip(),
        content=item_in.content,
        source=item_in.source,
        source_url=item_in.source_url,
        tags=item_in.tags,
        is_active=item_in.is_active,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/knowledge/{item_id}", response_model=KnowledgeResponse)
def get_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Retrieves a single knowledge item by ID (Admin Only)."""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")
    return item


@router.put("/knowledge/{item_id}", response_model=KnowledgeResponse)
def update_knowledge_item(
    item_id: int,
    item_in: KnowledgeUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Updates an existing knowledge item without model retraining (Admin Only)."""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")

    update_data = item_in.model_dump(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        update_data["category"] = update_data["category"].lower().strip()

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/knowledge/{item_id}", status_code=status.HTTP_200_OK)
def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Permanently deletes a knowledge item (Admin Only)."""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")

    db.delete(item)
    db.commit()
    return {"message": f"Knowledge item #{item_id} deleted successfully"}


@router.patch("/knowledge/{item_id}/toggle-status", response_model=KnowledgeResponse)
def toggle_knowledge_status(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Toggles active/archived status of a knowledge item (Admin Only)."""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")

    item.is_active = not item.is_active
    db.commit()
    db.refresh(item)
    return item


@router.get("/feedback-stats")
def get_feedback_and_query_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Retrieves aggregated query metrics and student feedback ratings (Admin Only)."""
    total_queries = db.query(StudentQuery).count()
    resolved_queries = db.query(StudentQuery).filter(StudentQuery.is_resolved.is_(True)).count()
    helpful_count = db.query(StudentQuery).filter(StudentQuery.feedback_rating == "HELPFUL").count()
    unhelpful_count = db.query(StudentQuery).filter(StudentQuery.feedback_rating == "UNHELPFUL").count()
    total_feedback = helpful_count + unhelpful_count

    satisfaction_rate = round((helpful_count / total_feedback * 100), 1) if total_feedback > 0 else 100.0

    return {
        "total_queries": total_queries,
        "resolved_queries": resolved_queries,
        "unresolved_queries": total_queries - resolved_queries,
        "resolution_rate": round((resolved_queries / total_queries * 100), 1) if total_queries > 0 else 100.0,
        "helpful_feedback": helpful_count,
        "unhelpful_feedback": unhelpful_count,
        "satisfaction_rate": satisfaction_rate,
    }
