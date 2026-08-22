"""
Monitoring and health check utilities.
"""
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models import AuditLog, Note
from typing import Dict, Any

try:
    import psutil  # optional; real system metrics when installed
except ImportError:  # pragma: no cover - metrics degrade gracefully without it
    psutil = None


class MonitoringService:
    """Service for monitoring and health checks."""

    def __init__(self, db: Session):
        self.db = db

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        try:
            # Database connectivity
            db_status = self._check_database()
            
            # Recent activity
            recent_activity = self._get_recent_activity()
            
            # System metrics
            metrics = self._get_system_metrics()
            
            return {
                "status": "healthy" if db_status else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": db_status,
                    "recent_activity": recent_activity,
                    "metrics": metrics
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _check_database(self) -> bool:
        """Check database connectivity."""
        try:
            # SQLAlchemy 2.0 requires raw SQL to be wrapped in text().
            self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity metrics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        # Audit logs — the AuditLog model's column is `timestamp`, not `created_at`.
        audit_last_hour = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= last_hour
        ).count()

        audit_last_day = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= last_day
        ).count()
        
        # Notes
        note_count = self.db.query(Note).count()
        
        return {
            "audit_logs_last_hour": audit_last_hour,
            "audit_logs_last_day": audit_last_day,
            "total_notes": note_count
        }

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics via psutil when available, else 'N/A'."""
        if psutil is None:
            return {"uptime": "N/A", "memory": "N/A", "cpu": "N/A"}

        try:
            boot = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = int((datetime.now() - boot).total_seconds())
            vm = psutil.virtual_memory()
            return {
                "uptime_seconds": uptime_seconds,
                "memory_percent": vm.percent,
                "memory_used_mb": round(vm.used / (1024 * 1024), 1),
                "cpu_percent": psutil.cpu_percent(interval=None),
            }
        except Exception:
            return {"uptime": "N/A", "memory": "N/A", "cpu": "N/A"}
