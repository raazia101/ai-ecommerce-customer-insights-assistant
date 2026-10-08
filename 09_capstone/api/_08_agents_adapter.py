"""
Adapter between the Week 10 conversation layer and the Week 9 agent.

The adapter isolates Week 10 from the internal implementation details
of the Week 9 agent workflow.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

AGENT_WORKFLOW_PATH = (
    PROJECT_ROOT
    / "08_agents"
    / "agent_workflow.py"
)


# ============================================================
# Week 9 module loading
# ============================================================

def _load_agent_module():
    """
    Dynamically load the existing Week 9 agent workflow.

    The project contains numbered directories such as 08_agents,
    which cannot be imported using a normal Python dotted import.
    """

    module_name = "week9_agent_workflow"

    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(
        module_name,
        AGENT_WORKFLOW_PATH,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load Week 9 agent from "
            f"{AGENT_WORKFLOW_PATH}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ============================================================
# Public adapter
# ============================================================

def run_agent(
    message: str,
    session_turns: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Execute the existing Week 9 run_agent() function.

    Args:
        message:
            Current user message.

        session_turns:
            Recent Week 10 conversation turns.

            The Week 9 deterministic baseline currently operates
            on the current question. Session context remains owned
            by the Week 10 conversation layer.

    Returns:
        Normalized result dictionary consumed by ConversationService.
    """

    # The current Week 9 deterministic workflow does not accept
    # session history as an argument.
    del session_turns

    agent_module = _load_agent_module()

    week9_run_agent = getattr(
        agent_module,
        "run_agent",
    )

    result = week9_run_agent(message)

    return _normalize_agent_result(result)


# ============================================================
# Result normalization
# ============================================================

def _normalize_agent_result(
    result: Any,
) -> dict[str, Any]:
    """
    Convert the Week 9 result into the Week 10 result contract.
    """

    if not isinstance(result, dict):
        return {
            "response": (
                "I couldn't produce a response for "
                "that request."
            ),
            "status": "tool_error",
            "tool_used": None,
            "sources": [],
        }

    answer = result.get(
        "answer",
        "",
    )

    selected_tool = result.get(
        "selected_tool"
    )

    success = bool(
        result.get(
            "success",
            False,
        )
    )

    errors = result.get(
        "errors",
        []
    )

    # --------------------------------------------------------
    # Status mapping
    # --------------------------------------------------------

    if success:
        status = "success"

    elif selected_tool is None:
        status = "unsupported"

    elif errors:
        status = "tool_error"

    else:
        status = "tool_error"

    # --------------------------------------------------------
    # Source/evidence extraction
    # --------------------------------------------------------

    sources = []

    tool_result = result.get(
        "tool_result"
    )

    if isinstance(tool_result, dict):
        raw_sources = tool_result.get(
            "sources",
            []
        )

        if isinstance(raw_sources, list):
            sources = raw_sources

    return {
        "response": str(answer),
        "status": status,
        "tool_used": selected_tool,
        "sources": sources,
    }
