"""
FastAPI entry point for the Week 10 conversational application.

Week 11 adds production-oriented observability around the existing API
without changing the application contract.

This module exposes:
    GET    /health
    POST   /chat
    DELETE /chat/{session_id}
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request

from .conversation import ConversationService
from .models import ChatRequest, ChatResponse, HealthResponse


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger("capstone.api")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="E-commerce Customer Insights Assistant",
    description=(
        "Week 10 conversational application layer integrating "
        "the Week 8 RAG pipeline and Week 9 controlled agent."
    ),
    version="1.0.0",
)


conversation_service = ConversationService()


# ---------------------------------------------------------------------------
# Request observability middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """
    Log request metadata and latency.

    A unique request trace ID is generated for every HTTP request.
    The request body is intentionally not logged to avoid exposing
    user-provided content.
    """

    request_trace_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    request.state.request_trace_id = request_trace_id

    try:
        response = await call_next(request)

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        response.headers["X-Request-Trace-ID"] = request_trace_id

        logger.info(
            "request_completed "
            "request_trace_id=%s method=%s path=%s "
            "status=%s latency_ms=%.2f",
            request_trace_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        return response

    except Exception:
        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "request_failed "
            "request_trace_id=%s method=%s path=%s "
            "latency_ms=%.2f",
            request_trace_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )

        raise


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    """Return the API health status."""

    return HealthResponse(status="ok")


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: Request,
    payload: ChatRequest,
) -> ChatResponse:
    """Process a conversational request."""

    request_trace_id = getattr(
        request.state,
        "request_trace_id",
        "unknown",
    )

    logger.info(
        "chat_started request_trace_id=%s",
        request_trace_id,
    )

    conversation_trace_id, result = conversation_service.chat(
        session_id=payload.session_id,
        message=payload.message,
    )

    logger.info(
        "chat_completed "
        "request_trace_id=%s conversation_trace_id=%s "
        "status=%s tool_used=%s",
        request_trace_id,
        conversation_trace_id,
        result.status,
        result.tool_used,
    )

    return ChatResponse(
        session_id=payload.session_id,
        trace_id=conversation_trace_id,
        response=result.response,
        sources=result.sources,
        tool_used=result.tool_used,
        status=result.status,
    )


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

@app.delete(
    "/chat/{session_id}",
)
def clear_chat(session_id: str) -> dict[str, str]:
    """Clear the conversation session."""

    conversation_service.clear_session(session_id)

    logger.info(
        "session_cleared session_id=%s",
        session_id,
    )

    return {
        "session_id": session_id,
        "status": "cleared",
    }