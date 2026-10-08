"""
FastAPI entry point for the Week 10 conversational application.

This module exposes:
    GET    /health
    POST   /chat
    DELETE /chat/{session_id}
"""

from fastapi import FastAPI

from .conversation import ConversationService
from .models import ChatRequest, ChatResponse, HealthResponse


app = FastAPI(
    title="E-commerce Customer Insights Assistant",
    description=(
        "Week 10 conversational application layer integrating "
        "the Week 8 RAG pipeline and Week 9 controlled agent."
    ),
    version="1.0.0",
)


conversation_service = ConversationService()


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    """Return the API health status."""

    return HealthResponse(status="ok")


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest) -> ChatResponse:
    """Process a conversational request."""

    trace_id, result = conversation_service.chat(
        session_id=request.session_id,
        message=request.message,
        )
    return ChatResponse(
        session_id=request.session_id,
        trace_id=trace_id,
        response=result.response,
        sources=result.sources,
        tool_used=result.tool_used,
        status=result.status,
        )


@app.delete(
    "/chat/{session_id}",
)
def clear_chat(session_id: str) -> dict[str, str]:
    """Clear the conversation session."""

    conversation_service.clear_session(session_id)

    return {
        "session_id": session_id,
        "status": "cleared",
    }
