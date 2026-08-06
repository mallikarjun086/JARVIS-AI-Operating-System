"""
FastAPI Endpoints for AI Core REST & SSE Streaming Completions.
Includes request size validation, prompt limits, and masked observability.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.ai.conversation import conversation_manager
from app.ai.prompts import prompt_manager
from app.ai.router import llm_router
from app.ai.schemas import CostMetrics, LLMMessage, LLMRequest, LLMResponse, MessageRole, ModelInfo
from app.api.deps import get_current_user
from app.config import settings
from app.core.logging import logger
from app.models.user import User

router = APIRouter()

# ─────────────────────────────────────────────────
# Request validation helpers
# ─────────────────────────────────────────────────

def _validate_request_size(request: LLMRequest) -> None:
    """Enforces maximum message count and total prompt byte size."""
    if len(request.messages) > settings.MAX_CONTEXT_MESSAGES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Request contains {len(request.messages)} messages; maximum allowed is {settings.MAX_CONTEXT_MESSAGES}."
        )
    total_bytes = sum(len(m.content.encode("utf-8")) for m in request.messages)
    if total_bytes > settings.MAX_PROMPT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Prompt payload {total_bytes} bytes exceeds maximum allowed {settings.MAX_PROMPT_BYTES} bytes."
        )


# ─────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────

@router.post("/chat/completions", response_model=LLMResponse, summary="Non-Streaming Chat Completion")
async def create_chat_completion(
    request: LLMRequest,
    session_id: Optional[str] = Query(None, description="Optional conversation session ID"),
    template_name: Optional[str] = Query(None, description="Optional prompt template name"),
    current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Executes an LLM chat completion through Conversation Manager,
    Prompt Manager, and LLM Router with request validation.
    """
    # 0. Validate request size
    _validate_request_size(request)

    # 1. Fetch or create session
    session = await conversation_manager.get_or_create_session(
        session_id=session_id,
        system_prompt=request.system_prompt
    )

    # 2. Render prompt if template specified
    if template_name and request.messages:
        user_text = request.messages[-1].content
        rendered_user, rendered_system = prompt_manager.render_prompt(
            template_name,
            user_input=user_text
        )
        if rendered_system and not request.system_prompt:
            request.system_prompt = rendered_system
        request.messages[-1].content = rendered_user

    # 3. Append last message turn to session
    if request.messages:
        session.add_user_message(request.messages[-1].content)

    # 4. Truncate context window to fit model context token budget
    model_info = llm_router.MODEL_REGISTRY.get(request.model)
    max_tokens = model_info.max_context_tokens if model_info else 4096
    session.truncate_context_window(max_context_tokens=max_tokens)

    # 5. Route request to provider
    routed_request = LLMRequest(
        model=request.model,
        messages=session.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        system_prompt=request.system_prompt,
        stream=False
    )

    try:
        response = await llm_router.generate_completion(routed_request)
    except asyncio.CancelledError:
        logger.warning("Chat completion request cancelled by client")
        raise HTTPException(status_code=499, detail="Request cancelled by client")

    # 6. Save assistant response to session
    session.add_assistant_message(response.content)

    return response


@router.post("/chat/stream", summary="Real-Time Server-Sent Events (SSE) Streaming Completion")
async def create_streaming_completion(
    request: LLMRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Executes streaming completion emitting real-time Server-Sent Events (SSE).
    Handles client disconnection gracefully.
    """
    _validate_request_size(request)

    async def sse_event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in llm_router.generate_stream(request):
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
        except asyncio.CancelledError:
            logger.info("SSE stream cancelled by client disconnect")
        except Exception as e:
            logger.error("SSE stream error", error=str(e))
            yield f"data: {json.dumps({'error': 'Stream error occurred'})}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.get("/models", response_model=List[ModelInfo], summary="List Registered LLM Models")
async def list_models(
    current_user: User = Depends(get_current_user)
) -> List[ModelInfo]:
    """Lists registered models across OpenAI, Claude, Gemini, and Mock providers."""
    return llm_router.list_available_models()


@router.get("/health", response_model=Dict[str, bool], summary="AI Provider Health Status")
async def get_ai_health(
    current_user: User = Depends(get_current_user)
) -> Dict[str, bool]:
    """Returns live health status for all registered LLM providers."""
    return await llm_router.health_check_all()


@router.get("/metrics", response_model=CostMetrics, summary="Get AI Core Cost & Token Telemetry")
async def get_ai_metrics(
    current_user: User = Depends(get_current_user)
) -> CostMetrics:
    """Returns cumulative token consumption and financial cost metrics."""
    return llm_router.get_metrics()
