
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import init_db, SessionLocal
from app.db.seed_knowledge import seed_knowledge_base
from app.models.user import User, UserRole
from app.api.v1 import api_router
from app.api.v1.health import router as root_health_router


def seed_database():
    db: Session = SessionLocal()

    try:
        admin_email = settings.FIRST_ADMIN_EMAIL.strip().lower()

        admin_user = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if admin_user is None:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(
                    settings.FIRST_ADMIN_PASSWORD
                ),
                full_name=settings.FIRST_ADMIN_NAME,
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(admin_user)
            print(f"[*] Initial Admin created: {admin_email}")

        else:
            admin_user.hashed_password = get_password_hash(
                settings.FIRST_ADMIN_PASSWORD
            )
            admin_user.full_name = settings.FIRST_ADMIN_NAME
            admin_user.role = UserRole.ADMIN
            admin_user.is_active = True

            print(
                f"[*] Admin credentials synchronized: {admin_email}"
            )

        db.commit()

        print("[*] Admin account is ready.")

        # Seed initial verified knowledge items
        seed_knowledge_base(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()

    # Create or synchronize the configured admin account
    seed_database()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Student Query Resolution Platform Backend API "
        "using FastAPI"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(root_health_router)
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "documentation": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }
