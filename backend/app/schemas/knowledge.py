from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class KnowledgeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    category: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=10)
    source: str = Field(default="", min_length=0, max_length=255)
    source_name: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, max_length=255)
    is_active: bool = True

    @model_validator(mode="before")
    @classmethod
    def reconcile_source(cls, values):
        if isinstance(values, dict):
            src = values.get("source") or values.get("source_name") or "Institutional Document"
            values["source"] = src
            values["source_name"] = src
        return values


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    content: Optional[str] = Field(None, min_length=10)
    source: Optional[str] = Field(None, max_length=255)
    source_name: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_source(cls, values):
        if isinstance(values, dict):
            if "source_name" in values and "source" not in values:
                values["source"] = values["source_name"]
            elif "source" in values and "source_name" not in values:
                values["source_name"] = values["source"]
        return values


class KnowledgeResponse(KnowledgeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
