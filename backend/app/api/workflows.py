"""
Workflow endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    WorkflowRequest,
    WorkflowResponse,
    CostConfirmationRequest,
    CostConfirmationResponse,
    CompactionRequest,
    CompactionResponse,
)
from app.services.llm.factory import LLMProviderFactory
from app.services.workflows.factory import WorkflowFactory
from app.services.github_branch_service import GitHubBranchService
from app.services.cost_service import CostService
from app.services.cost_enforcement import CostEnforcementService
from app.services.output_service import OutputService
from app.config import settings
from app.utils.logger import log_event
from app.utils.auth import require_admin

router = APIRouter()


@router.post("/workflows", response_model=WorkflowResponse)
async def run_workflow(
    request: WorkflowRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Run a workflow."""
    try:
        # Create LLM provider
        llm_provider = LLMProviderFactory.create_provider(
            provider=settings.llm_provider,
            api_key=settings.llm_api_key,
            model=settings.llm_model
        )

        # Create workflow
        workflow = WorkflowFactory.create_workflow(
            request.workflow_type,
            db,
            llm_provider
        )

        # Build context
        context = {
            "content": request.content,
            "context_query": request.context_query or "",
            "resources": request.resources or "",
            "constraints": request.constraints or "",
            "stakeholders": request.stakeholders or ""
        }

        # Execute workflow
        result = await workflow.execute(context)

        # Generate output with metadata
        output_service = OutputService()
        output_with_metadata = output_service.generate_output(
            workflow=request.workflow_type,
            content=result["content"],
            source_notes=result["source_notes"],
            llm_calls=result["llm_calls"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"]
        )

        # Record cost
        cost_service = CostService(db)
        cost_service.record_cost(
            workflow=request.workflow_type,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"]
        )

        return WorkflowResponse(
            workflow_id=f"{request.workflow_type}-{result['provider']}",
            status="completed",
            content=output_with_metadata,
            source_notes=result["source_notes"],
            llm_calls=result["llm_calls"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"]
        )

    except Exception as e:
        log_event(db, "workflow.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/compaction", response_model=CompactionResponse)
async def run_compaction(
    request: CompactionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Compile a topic's source notes into a derived wiki page (Karpathy pattern).

    Runs the compaction workflow, records cost, and (unless dry_run) opens a PR
    that adds the compiled page under 14 Agent Outputs/ — sources are never
    mutated and nothing is committed directly to main. dry_run returns the
    content for preview without touching git.
    """
    try:
        llm_provider = LLMProviderFactory.create_provider(
            provider=settings.llm_provider,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
        workflow = WorkflowFactory.create_workflow("compaction", db, llm_provider)

        result = await workflow.execute({"context_query": request.topic})

        # Record cost like the generic workflow path does.
        CostService(db).record_cost(
            workflow="compaction",
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"],
        )

        title = request.title or f"Wiki: {request.topic}"

        # Attach provenance metadata to the output (same helper the other
        # workflows use for their PR bodies).
        output_service = OutputService()
        content_with_metadata = output_service.generate_output(
            workflow="compaction",
            content=result["content"],
            source_notes=result["source_notes"],
            llm_calls=result["llm_calls"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"],
        )

        response = CompactionResponse(
            status="completed",
            topic=request.topic,
            content=content_with_metadata,
            source_notes=result["source_notes"],
            estimated_cost_usd=result["estimated_cost_usd"],
            model=result["model"],
            provider=result["provider"],
        )

        if request.dry_run:
            response.status = "dry_run"
            return response

        # Open a PR that adds the compiled page under 14 Agent Outputs/.
        github_service = GitHubBranchService(db)
        pr = github_service.complete_workflow_branch(
            workflow_type="compaction",
            content=content_with_metadata,
            title=title,
            metadata={
                "topic": request.topic,
                "source_notes": result["source_notes"],
                "model": result["model"],
                "estimated_cost_usd": result["estimated_cost_usd"],
            },
        )
        response.pr_number = pr["pr_number"]
        response.pr_url = pr["pr_url"]
        response.branch_name = pr["branch_name"]
        response.file_path = pr["file_path"]
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_event(db, "compaction.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/cost-check", response_model=CostConfirmationResponse)
async def check_workflow_cost(
    request: CostConfirmationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Check cost before executing research workflow."""
    try:
        cost_enforcement = CostEnforcementService(db)
        budget_check = cost_enforcement.check_research_budget(request.estimated_cost_usd)

        return CostConfirmationResponse(
            can_proceed=budget_check["can_proceed"],
            current_research_cost=budget_check["current_research_cost"],
            estimated_cost=budget_check["estimated_cost"],
            remaining_budget=budget_check["remaining_budget"],
            research_budget=budget_check["research_budget"],
            warning_level=budget_check["warning_level"]
        )

    except Exception as e:
        log_event(db, "cost_check.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
