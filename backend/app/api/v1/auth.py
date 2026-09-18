from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_student, get_current_admin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    # Public registration only creates STUDENT accounts for security
    # Admin accounts are provisioned securely via system seed / admin dashboard
    assigned_role = UserRole.STUDENT
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=assigned_role,
        student_id=user_in.student_id,
        department=user_in.department,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact administration."
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return current_user


@router.get("/test-student", tags=["RBAC Test"])
def test_student_role(current_user: User = Depends(get_current_student)):
    """Endpoint accessible only by authenticated users with STUDENT role."""
    return {
        "message": "Access granted to Student-only resource.",
        "user": current_user.email,
        "role": current_user.role.value
    }


@router.get("/test-admin", tags=["RBAC Test"])
def test_admin_role(current_user: User = Depends(get_current_admin)):
    """Endpoint accessible only by authenticated users with ADMIN role."""
    return {
        "message": "Access granted to Admin-only resource.",
        "user": current_user.email,
        "role": current_user.role.value
    }
