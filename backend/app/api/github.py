"""
GitHub integration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GitHubWorkflowRequest, GitHubWorkflowResponse
from app.services.github_branch_service import GitHubBranchService
from app.utils.logger import log_event
from app.utils.auth import require_admin

router = APIRouter()


@router.post("/github/workflow", response_model=GitHubWorkflowResponse)
async def complete_github_workflow(
    request: GitHubWorkflowRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Complete GitHub workflow: branch, write, commit, push, PR."""
    try:
        github_service = GitHubBranchService(db)

        result = github_service.complete_workflow_branch(
            workflow_type=request.workflow_type,
            content=request.content,
            title=request.title,
            metadata=request.metadata
        )

        return GitHubWorkflowResponse(
            status="completed",
            branch_name=result["branch_name"],
            file_path=result["file_path"],
            pr_number=result["pr_number"],
            pr_url=result["pr_url"]
        )

    except Exception as e:
        log_event(db, "github.workflow_failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/webhook")
async def github_webhook(payload: dict, db: Session = Depends(get_db)):
    """Handle GitHub webhook events."""
    event_type = payload.get("action", "unknown")

    if event_type in ["opened", "closed", "reopened"]:
        pr_number = payload.get("pull_request", {}).get("number")
        log_event(db, "github.webhook_received", {
            "event_type": event_type,
            "pr_number": pr_number
        })

    return {"status": "received"}
