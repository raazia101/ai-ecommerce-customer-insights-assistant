"""
API request and response models for the Week 10 application layer.

This module defines the public data contracts used by the FastAPI
chat application.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from the client."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier for the current conversation session.",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural-language user message.",
    )


class Source(BaseModel):
    """Source or evidence attached to a response."""

    source: str = Field(
        ...,
        description="Source identifier or document reference.",
    )

    relevance: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional relevance score.",
    )


class ChatResponse(BaseModel):
    """Structured response returned by the chat API."""

    session_id: str = Field(
        ...,
        description="Conversation session identifier.",
    )

    trace_id: str = Field(
        ...,
        description="Identifier used to trace the request through the system.",
    )

    response: str = Field(
        ...,
        description="User-facing assistant response.",
    )

    sources: list[Source] = Field(
        default_factory=list,
        description="Sources or evidence supporting the response.",
    )

    tool_used: str | None = Field(
        default=None,
        description="Approved tool used during request processing.",
    )

    status: Literal[
        "success",
        "clarification",
        "unsupported",
        "insufficient_evidence",
        "tool_error",
        "validation_error",
    ] = Field(
        ...,
        description="Final status of the conversation request.",
    )


class HealthResponse(BaseModel):
    """Health-check response."""

    status: Literal["ok"] = "ok"
