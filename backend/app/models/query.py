from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.db.base import Base


class StudentQuery(Base):
    __tablename__ = "student_queries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    sources_cited = Column(Text, nullable=True)  # JSON-encoded array of citations
    is_resolved = Column(Boolean, default=True, nullable=False)
    feedback_rating = Column(String(20), nullable=True)  # "HELPFUL", "UNHELPFUL"
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<StudentQuery(id={self.id}, student_id={self.student_id}, resolved={self.is_resolved})>"
