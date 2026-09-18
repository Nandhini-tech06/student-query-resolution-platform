from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.db.session import check_db_connection

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    db_status = check_db_connection()
    is_healthy = db_status.get("status") == "connected"
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status
    }
