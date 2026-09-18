from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db, SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.api.v1 import api_router
from app.api.v1.health import router as root_health_router


from app.db.seed_knowledge import seed_knowledge_base


def seed_database():
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.email == settings.FIRST_ADMIN_EMAIL).first()
        if not admin_exists:
            admin_user = User(
                email=settings.FIRST_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                full_name=settings.FIRST_ADMIN_NAME,
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"[*] Initial Admin created: {settings.FIRST_ADMIN_EMAIL}")
        else:
            print(f"[*] Admin account exists: {settings.FIRST_ADMIN_EMAIL}")

        # Seed initial verified knowledge items
        seed_knowledge_base(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and default data is seeded
    init_db()
    seed_database()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Student Query Resolution Platform Backend API using FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(root_health_router)  # /health at root
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "documentation": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }
