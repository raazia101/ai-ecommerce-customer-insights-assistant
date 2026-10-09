"""
Week 10 conversation layer.

This module provides the application-layer boundary between the FastAPI
API and the controlled Week 9 agent workflow.

The conversation layer is responsible for:
- session-aware conversation handling
- clarification
- delegation to the Week 9 agent
- safe handling of unsupported requests
- converting agent results into the Week 10 response contract
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

@dataclass
class ConversationSession:
    """Temporary state associated with one chat session."""

    session_id: str
    turns: list[dict[str, str]] = field(default_factory=list)


class ConversationManager:
    """
    Manage conversation sessions for the Week 10 application layer.

    Session state is intentionally bounded and kept separate from the
    Week 9 durable memory implementation.
    """

    MAX_TURNS = 20

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create(self, session_id: str) -> ConversationSession:
        """Return an existing session or create a new one."""

        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(
                session_id=session_id
            )

        return self._sessions[session_id]

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """Add one completed conversational turn."""

        session = self.get_or_create(session_id)

        session.turns.append(
            {
                "user": user_message,
                "assistant": assistant_message,
            }
        )

        # Keep only the most recent turns.
        if len(session.turns) > self.MAX_TURNS:
            session.turns = session.turns[-self.MAX_TURNS :]

    def clear(self, session_id: str) -> None:
        """Clear temporary session context."""

        self._sessions.pop(session_id, None)


# ---------------------------------------------------------------------------
# Conversation result
# ---------------------------------------------------------------------------

@dataclass
class ConversationResult:
    """Internal result produced by the conversation layer."""

    response: str
    status: str
    tool_used: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Conversation service
# ---------------------------------------------------------------------------

class ConversationService:
    """
    Application-level conversation service.

    The service delegates supported requests to the Week 9 controlled
    agent workflow.
    """

    def __init__(self) -> None:
        self.sessions = ConversationManager()

    def chat(
        self,
        session_id: str,
        message: str,
    ) -> tuple[str, ConversationResult]:
        """
        Process one conversational turn.

        Returns:
            A trace ID and a structured ConversationResult.
        """

        trace_id = str(uuid.uuid4())

        session = self.sessions.get_or_create(session_id)

        # Store the incoming message only after validation.
        message = message.strip()

        if not message:
            return trace_id, ConversationResult(
                response="Please provide a message.",
                status="validation_error",
            )

        # ---------------------------------------------------------------
        # Clarification handling
        # ---------------------------------------------------------------

        clarification = self._check_for_clarification(
            message=message,
            session=session,
        )

        if clarification is not None:
            self.sessions.add_turn(
                session_id=session_id,
                user_message=message,
                assistant_message=clarification.response,
            )

            return trace_id, clarification

        # ---------------------------------------------------------------
        # Unsupported / destructive request handling
        # ---------------------------------------------------------------

        if self._is_unsupported_or_destructive(message):
            result = ConversationResult(
                response=(
                    "I can help with customer lookups, order status, "
                    "KPI questions, and documentation-based questions. "
                    "I cannot perform destructive actions such as "
                    "cancelling orders, issuing refunds, or deleting data."
                ),
                status="unsupported",
            )

            self.sessions.add_turn(
                session_id=session_id,
                user_message=message,
                assistant_message=result.response,
            )

            return trace_id, result

        # ---------------------------------------------------------------
                # Delegate to Week 9 agent
        # ---------------------------------------------------------------

        try:
            resolved_message = self._resolve_context(
                message=message,
                session=session,
            )

            result = self._run_agent(
                message=resolved_message,
                session=session,
            )
        except Exception:
            result = ConversationResult(
                response="The assistant service encountered an internal error. Please try again.",
                status="tool_error",
                )

        self.sessions.add_turn(
            session_id=session_id,
            user_message=message,
            assistant_message=result.response,
        )

        return trace_id, result

    def clear_session(self, session_id: str) -> None:
        """Clear all conversation state for a session."""
        self.sessions.clear(session_id)

    # ------------------------------------------------------------------
    # Clarification
    # ------------------------------------------------------------------

    def _check_for_clarification(
            self,
            message: str,
            session: ConversationSession,
    ) -> ConversationResult | None:
        """Return a clarification response when required."""

        lowered = message.lower().strip()

        # A status question without an order ID requires clarification.
        is_status_question = "status" in lowered
        has_order_id = "ord-" in lowered
        has_recent_order = self._has_recent_order_context(session)

        if (
            is_status_question
            and not has_order_id
            and not has_recent_order
        ):
            return ConversationResult(
                response=(
                    "Sure â€” which order ID would you like me to check? "
                    "For example, ORD-00001."
                ),
                status="clarification",
            )

        return None

    @staticmethod
    def _has_recent_order_context(
        session: ConversationSession,
    ) -> bool:
        """Check whether recent conversation contains an order ID."""

        for turn in reversed(session.turns[-3:]):
            text = f"{turn['user']} {turn['assistant']}".upper()

            if "ORD-" in text:
                return True

        return False
        # ------------------------------------------------------------------
    # Context resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_context(
        message: str,
        session: ConversationSession,
    ) -> str:
        """
        Resolve simple conversational references using recent session
        context before delegating to the Week 9 deterministic agent.
        """

        import re

        lowered = message.lower()

        # Only resolve references when the current message does not
        # already contain an explicit order ID.
        if "ord-" in lowered:
            return message

        # Conversational references that can refer to the most recent
        # order discussed in the session.
        reference_patterns = (
            "that order",
            "this order",
            "the order",
            "that one",
            "this one",
        )

        if not any(
            pattern in lowered
            for pattern in reference_patterns
        ):
            return message

        # Search recent turns for the most recent order ID.
        for turn in reversed(session.turns[-3:]):
            text = f"{turn['user']} {turn['assistant']}"

            match = re.search(
                r"\bORD-\d{5}\b",
                text,
                flags=re.IGNORECASE,
            )

            if match:
                order_id = match.group(0).upper()

                return (
                    f"{message} "
                    f"The referenced order is {order_id}."
                )

        return message

    # ------------------------------------------------------------------
    # Safety / unsupported requests
    # ------------------------------------------------------------------

    @staticmethod
    def _is_unsupported_or_destructive(message: str) -> bool:
        """Detect requests outside the approved read-only capability set."""

        lowered = message.lower()

        destructive_patterns = (
            "cancel order",
            "cancel my order",
            "refund",
            "delete customer",
            "delete my data",
            "delete order",
            "remove customer",
            "modify order",
            "change order",
        )

        return any(
            pattern in lowered
            for pattern in destructive_patterns
        )

    # ------------------------------------------------------------------
    # Week 9 agent integration
    # ------------------------------------------------------------------

    @staticmethod
    def _run_agent(
        message: str,
        session: ConversationSession,
    ) -> ConversationResult:
        """
        Delegate a supported request to the Week 9 agent workflow.

        The exact adapter is kept isolated here so the FastAPI layer does
        not depend directly on Week 9 implementation details.
        """

        from pathlib import Path
        import sys

        project_root = Path(__file__).resolve().parents[2]

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ._08_agents_adapter import run_agent

        result = run_agent(
            message=message,
            session_turns=session.turns,
        )

        return ConversationResult(
            response=result["response"],
            status=result.get("status", "success"),
            tool_used=result.get("tool_used"),
            sources=result.get("sources", []),
        )
