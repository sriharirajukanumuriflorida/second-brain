"""
Cost tracking service.
"""
from sqlalchemy.orm import Session
from app.models import AuditLog
from typing import Dict, Any
import json


class CostService:
    """Service for tracking LLM costs."""

    def __init__(self, db: Session):
        self.db = db

    def record_cost(
        self,
        workflow: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd: float,
        model: str,
        provider: str
    ) -> None:
        """Record cost to audit log."""
        log_entry = AuditLog(
            event_type="llm.cost",
            event_data=json.dumps({
                "workflow": workflow,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost_usd": estimated_cost_usd,
                "model": model,
                "provider": provider
            })
        )
        self.db.add(log_entry)
        self.db.commit()

    def get_monthly_cost(self) -> Dict[str, Any]:
        """Get total cost for current month."""
        from datetime import datetime, timezone
        from sqlalchemy import func

        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        costs = self.db.query(AuditLog).filter(
            AuditLog.event_type == "llm.cost",
            AuditLog.timestamp >= start_of_month
        ).all()

        total_cost = 0.0
        total_tokens = 0
        by_workflow = {}

        for cost in costs:
            data = json.loads(cost.event_data)
            cost_usd = data.get("estimated_cost_usd", 0)
            workflow_name = data.get("workflow", "unknown")

            total_cost += cost_usd
            total_tokens += data.get("input_tokens", 0) + data.get("output_tokens", 0)

            if workflow_name not in by_workflow:
                by_workflow[workflow_name] = 0
            by_workflow[workflow_name] += cost_usd

        return {
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "by_workflow": by_workflow
        }
