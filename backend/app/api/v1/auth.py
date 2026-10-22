
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    get_current_user,
    get_current_student,
    get_current_admin,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_institute_email(email: str) -> bool:
    return bool(
        re.fullmatch(
            r"[a-zA-Z0-9._-]+@nip\.ac\.in",
            email.strip(),
            re.IGNORECASE,
        )
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    email = str(user_in.email).strip().lower()

    if not validate_institute_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be in the format name@nip.ac.in.",
        )

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    new_user = User(
        email=email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.STUDENT,
        student_id=user_in.student_id,
        department=user_in.department,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    email = str(credentials.email).strip().lower()

    if not validate_institute_email(email):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Use an institute email in the format name@nip.ac.in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact administration.",
        )

    role = (
        user.role.value
        if isinstance(user.role, UserRole)
        else str(user.role).upper()
    )

    access_token = create_access_token(
        subject=user.id,
        role=role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/test-student", tags=["RBAC Test"])
def test_student_role(
    current_user: User = Depends(get_current_student),
):
    return {
        "message": "Access granted to Student-only resource.",
        "user": current_user.email,
        "role": current_user.role.value,
    }


@router.get("/test-admin", tags=["RBAC Test"])
def test_admin_role(
    current_user: User = Depends(get_current_admin),
):
    return {
        "message": "Access granted to Admin-only resource.",
        "user": current_user.email,
        "role": current_user.role.value,
    }
