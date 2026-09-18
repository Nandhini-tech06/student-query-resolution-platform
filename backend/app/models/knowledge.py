from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.db.base import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    tags = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # One-to-many: a single knowledge document may have many retrieval chunks
    chunks = relationship(
        "KnowledgeChunk",
        back_populates="knowledge_item",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @hybrid_property
    def source_name(self) -> str:
        return self.source

    @source_name.setter
    def source_name(self, value: str):
        self.source = value

    @property
    def is_chunked(self) -> bool:
        """Returns True when at least one chunk exists for this item."""
        return self.chunks.count() > 0  # type: ignore[union-attr]

    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, title='{self.title}', category='{self.category}', source='{self.source}', active={self.is_active})>"
