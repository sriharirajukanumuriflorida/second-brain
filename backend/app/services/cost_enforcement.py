"""
Cost enforcement service for research workflows.
"""
from sqlalchemy.orm import Session
from app.services.cost_service import CostService
from app.config import settings
from typing import Dict, Any


class CostEnforcementService:
    """Service for enforcing cost limits on research workflows."""

    def __init__(self, db: Session):
        self.db = db
        self.cost_service = CostService(db)

    def check_research_budget(self, estimated_cost_usd: float) -> Dict[str, Any]:
        """Check if research workflow can proceed within budget."""
        # Research workflow budget: $1/month per ADR-009
        RESEARCH_BUDGET = 1.0

        # Get current monthly cost
        monthly_cost = self.cost_service.get_monthly_cost()
        current_research_cost = monthly_cost.get("by_workflow", {}).get("knowledge-refresh", 0)
        current_research_cost += monthly_cost.get("by_workflow", {}).get("technology-radar", 0)
        current_research_cost += monthly_cost.get("by_workflow", {}).get("research-gap-analysis", 0)

        # Check if within budget
        remaining_budget = RESEARCH_BUDGET - current_research_cost
        can_proceed = (current_research_cost + estimated_cost_usd) <= RESEARCH_BUDGET

        return {
            "can_proceed": can_proceed,
            "current_research_cost": current_research_cost,
            "estimated_cost": estimated_cost_usd,
            "remaining_budget": remaining_budget,
            "research_budget": RESEARCH_BUDGET,
            "warning_level": self._get_warning_level(current_research_cost, RESEARCH_BUDGET)
        }

    def _get_warning_level(self, current_cost: float, budget: float) -> str:
        """Get warning level based on budget usage."""
        usage_percent = (current_cost / budget) * 100

        if usage_percent >= 100:
            return "blocked"
        elif usage_percent >= 80:
            return "critical"
        elif usage_percent >= 50:
            return "warning"
        else:
            return "ok"

    def confirm_cost(self, workflow_type: str, estimated_cost_usd: float) -> bool:
        """Confirm cost before executing research workflow."""
        budget_check = self.check_research_budget(estimated_cost_usd)

        if not budget_check["can_proceed"]:
            return False

        return True
