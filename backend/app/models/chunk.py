from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class KnowledgeChunk(Base):
    """
    A text chunk derived from a KnowledgeItem document.

    Long documents are split into overlapping chunks at ingestion time.
    Each chunk is the unit of retrieval used by the RAG pipeline.
    Optionally stores a serialised float embedding for vector search.
    """
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    knowledge_item_id = Column(
        Integer,
        ForeignKey("knowledge_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)          # 0-based position in parent doc
    chunk_text = Column(Text, nullable=False)
    # Serialised as a JSON string: "[0.1, 0.3, …]" or empty string if not embedded
    embedding = Column(Text, nullable=True, default="")

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Back-reference to the parent knowledge item (lazy so we don't load it unless needed)
    knowledge_item = relationship(
        "KnowledgeItem",
        back_populates="chunks",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<KnowledgeChunk(id={self.id}, item_id={self.knowledge_item_id}, "
            f"index={self.chunk_index}, len={len(self.chunk_text)})>"
        )
