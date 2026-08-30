"""
Chat endpoint — POST /api/v1/chat
"""
import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, WebSource, LLMConfig, ChatModelsResponse
from app.models import ChatSession, ChatMessage
from app.services.llm.factory import LLMProviderFactory
from app.services.workflows.mentor_chat_workflow import MentorChatWorkflow
from app.services.cost_service import CostService
from app.config import settings
from app.utils.auth import require_read_access, Principal
from app.utils.logger import log_event

router = APIRouter()


async def _fetch_provider_models(provider: str, api_key: str) -> list[str]:
    provider = provider.lower()
    timeout = httpx.Timeout(15.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        if provider in {"anthropic", "claude"}:
            response = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            if response.status_code >= 400:
                raise HTTPException(status_code=400, detail="Failed to fetch Anthropic models.")
            payload = response.json()
            raw_models = payload.get("data", []) or payload.get("models", [])
            models = [
                m.get("id")
                for m in raw_models
                if isinstance(m, dict) and isinstance(m.get("id"), str)
            ]
            return sorted(set(models))

        if provider == "openai":
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if response.status_code >= 400:
                raise HTTPException(status_code=400, detail="Failed to fetch OpenAI models.")
            payload = response.json()
            raw_models = payload.get("data", [])
            models = [
                m.get("id")
                for m in raw_models
                if isinstance(m, dict) and isinstance(m.get("id"), str)
            ]
            return sorted(set(models))

    raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")


@router.post("/chat/models", response_model=ChatModelsResponse)
async def chat_models(
    request: LLMConfig,
    principal: Principal = Depends(require_read_access),
):
    """List provider models available to the supplied API key."""
    _ = principal
    models = await _fetch_provider_models(request.provider, request.api_key)
    return ChatModelsResponse(provider=request.provider.lower(), models=models)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Send a message to the LLM mentor.

    The LLM reads the vault as RAG context and may call native web search when
    vault notes are insufficient. Supports multi-turn conversation via session_id.

    An optional `llm_config` block allows users to supply their own provider/key/model.
    When absent the server's configured LLM credentials are used.
    """
    try:
        # Resolve LLM credentials: user-supplied override → server defaults
        if request.llm_config:
            provider_name = request.llm_config.provider
            api_key = request.llm_config.api_key
            model = request.llm_config.model or settings.llm_model
        else:
            provider_name = settings.llm_provider
            api_key = settings.llm_api_key
            model = settings.llm_model

        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="No LLM API key configured. Please provide one in the chat settings.",
            )

        llm_provider = LLMProviderFactory.create_provider(
            provider=provider_name,
            api_key=api_key,
            model=model,
        )

        # Resolve or create chat session
        session_id = request.session_id or str(uuid.uuid4())
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session is None:
            user_id = principal.user.id if principal.user else None
            session = ChatSession(id=session_id, user_id=user_id)
            db.add(session)
            db.commit()

        # Convert history to plain dicts for the workflow
        history = [{"role": m.role, "content": m.content} for m in request.history]

        # Execute mentor chat workflow
        workflow = MentorChatWorkflow(db, llm_provider)
        result = await workflow.execute({
            "message": request.message,
            "history": history,
            "enable_web_search": request.allow_web_search,
        })

        # Persist user + assistant messages
        db.add(ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message,
        ))
        import json
        db.add(ChatMessage(
            session_id=session_id,
            role="assistant",
            content=result["reply"],
            source_notes=json.dumps(result["source_notes"]),
            web_sources=json.dumps(result["web_sources"]),
            model=result["model"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        ))
        db.commit()

        # Track cost (skip if user supplied their own key — cost is theirs)
        if not request.llm_config and not result["cached"]:
            CostService(db).record_cost(
                workflow="mentor-chat",
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                estimated_cost_usd=result["estimated_cost_usd"],
                model=result["model"],
                provider=result["provider"],
            )

        return ChatResponse(
            reply=result["reply"],
            session_id=session_id,
            source_notes=result["source_notes"],
            web_sources=[WebSource(**s) for s in result["web_sources"] if s.get("url")],
            model=result["model"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            estimated_cost_usd=result["estimated_cost_usd"],
            cached=result["cached"],
        )

    except HTTPException:
        raise
    except Exception as e:
        if "`temperature` is deprecated for this model." in str(e):
            raise HTTPException(
                status_code=400,
                detail="Selected model does not support temperature. Please choose a different model in chat settings.",
            )
        log_event(db, "chat.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
