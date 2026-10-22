
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.STUDENT
    student_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_institute_email(cls, value: EmailStr) -> EmailStr:
        email = str(value).strip().lower()
        if not email.endswith("@nip.ac.in"):
            raise ValueError("Email must end with @nip.ac.in")
        return email


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        description="Password must be at least 6 characters",
    )
    full_name: str = Field(..., min_length=2, max_length=150)
    student_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = UserRole.STUDENT

    @field_validator("email")
    @classmethod
    def validate_institute_email(cls, value: EmailStr) -> EmailStr:
        email = str(value).strip().lower()
        if not email.endswith("@nip.ac.in"):
            raise ValueError("Email must end with @nip.ac.in")
        return email


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    student_id: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
