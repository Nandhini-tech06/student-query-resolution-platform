from typing import Generator, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User, UserRole


oauth2_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Get the actual JWT string from the HTTP Bearer credentials
        token = credentials.credentials

        # Decode and validate the JWT
        payload = decode_access_token(token)

        # Get user ID from the "sub" claim
        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

    except (jwt.PyJWTError, ValueError, TypeError):
        raise credentials_exception

    # Find the user in the database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    # Check whether the account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user


def require_role(allowed_roles: List[UserRole]):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access forbidden: requires one of "
                    f"[{', '.join(r.value for r in allowed_roles)}] roles"
                )
            )

        return current_user

    return role_checker


get_current_student = require_role([UserRole.STUDENT])

get_current_admin = require_role([UserRole.ADMIN])