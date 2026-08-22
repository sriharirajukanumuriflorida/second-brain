"""
Workflow factory.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.llm.base import BaseLLMProvider
from app.services.workflows.grill_me_workflow import GrillMeWorkflow
from app.services.workflows.implementation_plan_workflow import ImplementationPlanWorkflow
from app.services.workflows.solution_brief_workflow import SolutionBriefWorkflow
from app.services.workflows.knowledge_refresh_workflow import KnowledgeRefreshWorkflow
from app.services.workflows.technology_radar_workflow import TechnologyRadarWorkflow
from app.services.workflows.research_gap_workflow import ResearchGapWorkflow


class WorkflowFactory:
    """Factory for creating workflow instances."""

    @staticmethod
    def create_workflow(
        workflow_type: str,
        db: Session,
        llm_provider: BaseLLMProvider
    ):
        """Create workflow instance."""
        workflow_type = workflow_type.lower()

        if workflow_type == "grill-me" or workflow_type == "grill-me-review":
            return GrillMeWorkflow(db, llm_provider)
        elif workflow_type == "implementation-plan":
            return ImplementationPlanWorkflow(db, llm_provider)
        elif workflow_type == "solution-brief":
            return SolutionBriefWorkflow(db, llm_provider)
        elif workflow_type == "knowledge-refresh":
            return KnowledgeRefreshWorkflow(db, llm_provider)
        elif workflow_type == "technology-radar":
            return TechnologyRadarWorkflow(db, llm_provider)
        elif workflow_type == "research-gap" or workflow_type == "research-gap-analysis":
            return SolutionBriefWorkflow(db, llm_provider)
        else:
            raise ValueError(f"Unsupported workflow type: {workflow_type}")
