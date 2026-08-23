"""
Chat endpoint — POST /api/v1/chat
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, WebSource
from app.models import ChatSession, ChatMessage
from app.services.llm.factory import LLMProviderFactory
from app.services.workflows.mentor_chat_workflow import MentorChatWorkflow
from app.services.cost_service import CostService
from app.config import settings
from app.utils.auth import require_read_access, Principal
from app.utils.logger import log_event

router = APIRouter()


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
            "enable_web_search": True,
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
            cached=result["cached"],
        )

    except HTTPException:
        raise
    except Exception as e:
        log_event(db, "chat.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
