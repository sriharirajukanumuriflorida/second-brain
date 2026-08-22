"""
Monitoring and health check endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.monitoring import MonitoringService
from app.utils.auth import require_read_access, Principal

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint. Public on purpose (keep-alive pinger hits it)."""
    monitoring = MonitoringService(db)
    status = monitoring.get_health_status()
    return status


@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Get system metrics (dashboard). Requires login or read-only access."""
    monitoring = MonitoringService(db)
    status = monitoring.get_health_status()
    return status.get("checks", {})
