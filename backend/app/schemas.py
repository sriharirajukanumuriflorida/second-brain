"""
Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str = "0.1.0"


class SyncRequest(BaseModel):
    """Sync request."""

    force: bool = False


class SyncResponse(BaseModel):
    """Sync response."""

    sync_id: int
    status: str
    message: str


class StatusResponse(BaseModel):
    """Status response."""

    total_notes: int
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    vault_path: str


class NoteResponse(BaseModel):
    """Note response."""

    id: int
    path: str
    title: str
    tags: List[str] = []
    backlinks: List[str] = []
    folder: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_indexed_at: datetime


class FolderResponse(BaseModel):
    """Folder response."""

    name: str
    note_count: int


class SearchRequest(BaseModel):
    """Search request."""

    query: str = Field(..., min_length=1)
    folder: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    """Search result."""

    id: int
    path: str
    title: str
    snippet: Optional[str] = None
    score: float = 1.0


class WorkflowRequest(BaseModel):
    """Workflow request."""
    workflow_type: str
    content: str
    context_query: Optional[str] = None
    resources: Optional[str] = None
    constraints: Optional[str] = None
    stakeholders: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Workflow response."""
    workflow_id: str
    status: str
    content: str
    source_notes: list[str]
    llm_calls: int
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    model: str
    provider: str


class GitHubWorkflowRequest(BaseModel):
    """GitHub workflow request."""
    workflow_type: str
    content: str
    title: str
    metadata: dict = {}


class GitHubWorkflowResponse(BaseModel):
    """GitHub workflow response."""
    status: str
    branch_name: str
    file_path: str
    pr_number: int
    pr_url: str


class CostConfirmationRequest(BaseModel):
    """Cost confirmation request."""
    workflow_type: str
    estimated_cost_usd: float


class CostConfirmationResponse(BaseModel):
    """Cost confirmation response."""
    can_proceed: bool
    current_research_cost: float
    estimated_cost: float
    remaining_budget: float
    research_budget: float
    warning_level: str
