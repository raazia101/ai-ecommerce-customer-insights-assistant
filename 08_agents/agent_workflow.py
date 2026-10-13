"""
Week 9 - Stateful Agent Workflow

Implements a bounded, deterministic agent workflow for the
E-commerce Customer Insights Assistant.

Workflow:

    UNDERSTAND
        â†“
    SELECT_TOOL
        â†“
    EXECUTE_TOOL
        â†“
    EVALUATE_RESULT
        â†“
    SYNTHESIZE
        â†“
    VALIDATE
        â†“
    RESPOND
        â†“
    TERMINATE

The workflow is intentionally deterministic for this baseline so
that tool selection, retries, safety behavior, and termination
can be tested and audited.

Approved tools are read-only:

    customer_lookup
    order_status
    kpi_query
    documentation_search
"""

from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = PROJECT_ROOT / "08_agents"


# ============================================================
# Workflow configuration
# ============================================================

MAX_STEPS = 8
MAX_TOOL_RETRIES = 2
MAX_TRACE_RESULT_LENGTH = 500


# ============================================================
# Dynamic module loading
# ============================================================
#
# Python module names cannot begin with a number, so folders such
# as 07_llm_rag cannot be imported using a normal dotted import.
# Dynamic loading keeps the existing project structure unchanged.
#


def _load_module_from_path(
    module_name: str,
    file_path: Path,
):
    """
    Dynamically load a Python module from a filesystem path.
    """

    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module from {file_path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ============================================================
# Tool loading
# ============================================================

TOOLS_MODULE_PATH = AGENTS_DIR / "tools.py"

tools_module = _load_module_from_path(
    "week9_tools_module",
    TOOLS_MODULE_PATH,
)


TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "customer_lookup": tools_module.customer_lookup,
    "order_status": tools_module.order_status,
    "kpi_query": tools_module.kpi_query,
    "documentation_search": tools_module.documentation_search,
}


# ============================================================
# Workflow state
# ============================================================


class WorkflowState(Enum):
    """
    States used by the bounded agent workflow.
    """

    UNDERSTAND = "understand"
    SELECT_TOOL = "select_tool"
    EXECUTE_TOOL = "execute_tool"
    EVALUATE_RESULT = "evaluate_result"
    SYNTHESIZE = "synthesize"
    VALIDATE = "validate"
    RESPOND = "respond"
    TERMINATE = "terminate"


@dataclass
class AgentState:
    """
    Mutable state carried through the workflow.

    The state contains:

    - original user question
    - current workflow state
    - selected tool
    - tool arguments
    - tool result
    - final answer
    - step count
    - number of tool attempts
    - execution trace
    - errors
    - termination status
    """

    question: str

    current_state: WorkflowState = WorkflowState.UNDERSTAND

    selected_tool: str | None = None

    tool_args: dict[str, Any] = field(
        default_factory=dict
    )

    tool_result: dict[str, Any] | None = None

    final_answer: str = ""

    step_count: int = 0

    tool_attempts: int = 0

    trace: list[dict[str, Any]] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    terminated: bool = False


# ============================================================
# Trace helpers
# ============================================================


def _compact_value(
    value: Any,
    max_length: int = MAX_TRACE_RESULT_LENGTH,
) -> Any:
    """
    Convert large values into compact trace-safe values.

    Traces should remain useful for debugging without storing
    unnecessarily large tool outputs.
    """

    if isinstance(value, str):
        if len(value) <= max_length:
            return value

        return value[:max_length] + "...[truncated]"

    if isinstance(value, dict):
        compacted = {}

        for key, item in value.items():
            compacted[key] = _compact_value(
                item,
                max_length,
            )

        return compacted

    if isinstance(value, list):
        return [
            _compact_value(
                item,
                max_length,
            )
            for item in value[:10]
        ]

    return value


def _record_trace(
    state: AgentState,
    event: dict[str, Any],
) -> None:
    """
    Add a structured trace event.

    Every event records the current workflow state and step.
    """

    trace_event = {
        "step": state.step_count,
        "state": state.current_state.value,
        **_compact_value(event),
    }

    state.trace.append(trace_event)


# ============================================================
# Question normalization
# ============================================================


def _normalise_question(
    question: str,
) -> str:
    """
    Normalize a user question.

    Raises:
        ValueError: if the question is empty or invalid.
    """

    if not isinstance(question, str):
        raise ValueError(
            "Question must be a string."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    return question


# ============================================================
# Identifier extraction
# ============================================================


def _extract_identifier(
    question: str,
    prefix: str,
) -> str | None:
    """
    Extract an identifier such as:

        CUST-0001
        ORD-00001

    The number of digits is intentionally flexible because
    validation of whether the record exists belongs to the tool.
    """

    pattern = rf"\b{re.escape(prefix)}-\d+\b"

    match = re.search(
        pattern,
        question.upper(),
    )

    if not match:
        return None

    return match.group(0)


# ============================================================
# Understand request
# ============================================================


def understand_request(
    state: AgentState,
) -> None:
    """
    Validate and normalize the incoming request.
    """

    state.question = _normalise_question(
        state.question
    )

    _record_trace(
        state,
        {
            "event": "request_understood",
            "question": state.question,
        },
    )


# ============================================================
# KPI detection
# ============================================================

def _detect_kpi(
    question: str,
) -> str | None:
    """
    Detect one of the approved KPI names from natural language.
    """

    question = question.lower()

    kpi_patterns = {
        "kpi_summary": [
            "key business kpis",
            "key business kpi",
            "business kpis",
            "business kpi",
            "key kpis",
            "key performance indicators",
            "important kpis",
            "important business metrics",
        ],
        "top_product_revenue": [
            "products generate the most revenue",
            "products generate most revenue",
            "products with the most revenue",
            "top products by revenue",
            "highest product revenue",
            "top product revenue",
            "products make the most revenue",
        ],
        "top_selling_products": [
            "top selling products",
            "top-selling products",
            "top selling product",
            "best selling products",
            "best-selling products",
            "most sold products",
            "products sell the most",
        ],
        "payment_success_rate": [
            "payment success rate",
            "payment success",
            "successful payment rate",
        ],
        "completed_revenue": [
            "completed revenue",
            "total completed revenue",
            "total revenue",
            "revenue",
        ],
        "average_order_value": [
            "average order value",
            "aov",
            "average order",
        ],
        "repeat_purchase_rate": [
            "repeat purchase rate",
            "repeat-purchase rate",
            "customer repeat-purchase rate",
            "customer repeat purchase rate",
            "repeat purchase",
            "repeat customers",
            "repeat-purchase",
        ],
        "customer_value": [
            "customer value",
            "customer lifetime value",
            "customer value metric",
        ],
        "total_orders": [
            "total orders",
            "number of orders",
            "how many orders",
            "how many orders do we have",
            "orders do we have",
        ],
        "total_customers": [
            "total customers",
            "number of customers",
            "how many customers",
            "how many customers do we have",
            "customers do we have",
        ],
    }

    for kpi_name, patterns in kpi_patterns.items():
        if any(pattern in question for pattern in patterns):
            return kpi_name

    return None






# ============================================================
# Tool selection
# ============================================================


def select_tool(
    state: AgentState,
) -> None:
    """
    Select exactly one approved tool using deterministic routing.

    Deterministic routing is intentional for this baseline:
    it makes tool selection predictable, testable, and auditable.

    The approved tools are read-only.

    Requests attempting unsupported side effects are rejected
    before identifier-based routing occurs.
    """

    question_lower = state.question.lower()

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------
    #
    # The available tools cannot modify or delete business data.
    #
    # We intentionally match action-specific phrases rather than
    # individual words such as "refund" or "cancel".
    #
    # This means legitimate questions such as:
    #
    #   "What is the refund policy?"
    #   "What is the cancellation policy?"
    #
    # can still be routed to documentation_search.
    #

    destructive_patterns = [
        "delete customer",
        "remove customer",
        "modify customer",
        "change customer",
        "update customer",
        "edit customer",
        "delete order",
        "remove order",
        "modify order",
        "change order",
        "update order",
        "edit order",
        "cancel order",
        "refund order",
    ]

    if any(
        pattern in question_lower
        for pattern in destructive_patterns
    ):
        state.selected_tool = None
        state.tool_args = {}

        state.errors.append(
            "Request involves an unsupported side effect."
        )

        _record_trace(
            state,
            {
                "event": "tool_selection_rejected",
                "reason": "unsupported_side_effect",
            },
        )

        return

    # --------------------------------------------------------
    # Extract identifiers
    # --------------------------------------------------------

    customer_id = _extract_identifier(
        state.question,
        "CUST",
    )

    order_id = _extract_identifier(
        state.question,
        "ORD",
    )

    # --------------------------------------------------------
    # Customer lookup
    # --------------------------------------------------------

    if customer_id:
        state.selected_tool = "customer_lookup"

        state.tool_args = {
            "customer_id": customer_id,
        }

        _record_trace(
            state,
            {
                "event": "tool_selected",
                "tool": "customer_lookup",
                "reason": "customer_identifier_detected",
                "arguments": {
                    "customer_id": customer_id,
                },
            },
        )

        return

    # --------------------------------------------------------
    # Order status
    # --------------------------------------------------------

    if order_id:
        state.selected_tool = "order_status"

        state.tool_args = {
            "order_id": order_id,
        }

        _record_trace(
            state,
            {
                "event": "tool_selected",
                "tool": "order_status",
                "reason": "order_identifier_detected",
                "arguments": {
                    "order_id": order_id,
                },
            },
        )

        return

    # --------------------------------------------------------
    # KPI query
    # --------------------------------------------------------

    kpi_name = _detect_kpi(
        question_lower
    )

    if kpi_name:
        state.selected_tool = "kpi_query"

        state.tool_args = {
            "kpi_name": kpi_name,
        }

        _record_trace(
            state,
            {
                "event": "tool_selected",
                "tool": "kpi_query",
                "reason": "kpi_request_detected",
                "arguments": {
                    "kpi_name": kpi_name,
                },
            },
        )

        return

    # --------------------------------------------------------
    # Documentation / RAG search
    # --------------------------------------------------------

    documentation_terms = [
        "return",
        "returns",
        "refund",
        "refunds",
        "payment",
        "payments",
        "declined",
        "cancel",
        "cancellation",
        "policy",
        "policies",
        "delivery",
        "shipping",
        "customer support",
        "faq",
        "how long",
        "eligible",
        ]

    if any(
        term in question_lower
        for term in documentation_terms
    ):
        state.selected_tool = "documentation_search"

        state.tool_args = {
            "question": state.question,
        }

        _record_trace(
            state,
            {
                "event": "tool_selected",
                "tool": "documentation_search",
                "reason": "documentation_request_detected",
                "arguments": {
                    "question": state.question,
                },
            },
        )

        return

    # --------------------------------------------------------
    # Unsupported request
    # --------------------------------------------------------

    state.selected_tool = None
    state.tool_args = {}
    state.errors.append(
        "No approved tool can safely handle this request."
        )

    _record_trace(
        state,
        {
            "event": "tool_selection_rejected",
            "reason": "no_approved_tool",
        },
    )
    state.current_state = WorkflowState.SYNTHESIZE


# ============================================================
# Execute tool
# ============================================================


def execute_tool(
    state: AgentState,
) -> None:
    """
    Execute the selected approved tool.

    Tool attempts are bounded by MAX_TOOL_RETRIES.
    """

    if not state.selected_tool:
        state.tool_result = None

        _record_trace(
            state,
            {
                "event": "tool_execution_skipped",
                "reason": "no_tool_selected",
            },
        )

        state.current_state = WorkflowState.EVALUATE_RESULT
        return

    if state.selected_tool not in TOOL_FUNCTIONS:
        state.tool_result = {
            "success": False,
            "error": (
                f"Unsupported tool: "
                f"{state.selected_tool}"
            ),
        }

        state.errors.append(
            f"Unsupported tool: {state.selected_tool}"
        )

        _record_trace(
            state,
            {
                "event": "tool_execution_failed",
                "tool": state.selected_tool,
                "reason": "unknown_tool",
            },
        )

        state.current_state = WorkflowState.EVALUATE_RESULT
        return

    if state.tool_attempts >= MAX_TOOL_RETRIES:
        state.tool_result = {
            "success": False,
            "error": "Tool retry limit reached.",
        }

        state.errors.append(
            "Tool retry limit reached."
        )

        _record_trace(
            state,
            {
                "event": "tool_execution_blocked",
                "tool": state.selected_tool,
                "reason": "retry_limit",
            },
        )

        state.current_state = WorkflowState.EVALUATE_RESULT
        return

    state.tool_attempts += 1

    tool_name = state.selected_tool

    tool_function = TOOL_FUNCTIONS[
        tool_name
    ]

    _record_trace(
        state,
        {
            "event": "tool_execution_started",
            "tool": tool_name,
            "attempt": state.tool_attempts,
            "arguments": state.tool_args,
        },
    )

    try:
        result = tool_function(
            **state.tool_args
        )

        if not isinstance(result, dict):
            result = {
                "success": True,
                "result": result,
            }

        state.tool_result = result

        _record_trace(
            state,
            {
                "event": "tool_execution_completed",
                "tool": tool_name,
                "attempt": state.tool_attempts,
                "result": result,
            },
        )

    except Exception as exc:
        state.tool_result = {
            "success": False,
            "error": str(exc),
        }

        state.errors.append(
            f"{tool_name} failed: {exc}"
        )

        _record_trace(
            state,
            {
                "event": "tool_execution_failed",
                "tool": tool_name,
                "attempt": state.tool_attempts,
                "error": str(exc),
            },
        )

    # Move to result evaluation after every execution attempt.
    state.current_state = WorkflowState.EVALUATE_RESULT


# ============================================================
# Evaluate tool result
# ============================================================


def evaluate_result(
    state: AgentState,
) -> None:
    """
    Evaluate whether the tool result is usable.

    Failed tools may be retried, but retries are explicitly bounded.
    """

    if not state.selected_tool:
        _record_trace(
            state,
            {
                "event": "result_evaluation_skipped",
                "reason": "no_tool_selected",
            },
        )

        state.current_state = WorkflowState.SYNTHESIZE
        return

    result = state.tool_result

    if result is None:
        state.errors.append(
            "Tool returned no result."
        )

        _record_trace(
            state,
            {
                "event": "tool_result_invalid",
                "reason": "missing_result",
            },
        )

        state.current_state = WorkflowState.SYNTHESIZE
        return

    success = bool(
        result.get("success", False)
    )
        # --------------------------------------------------------
    # Valid "not found" lookup result
    # --------------------------------------------------------

    if (
        state.selected_tool == "customer_lookup"
        and result.get("found") is False
    ):
        _record_trace(
            state,
            {
                "event": "tool_result_accepted",
                "tool": state.selected_tool,
                "reason": "customer_not_found",
            },
        )

        state.current_state = WorkflowState.SYNTHESIZE
        return


    # --------------------------------------------------------
    # Successful result
    # --------------------------------------------------------

    if success:
        _record_trace(
            state,
            {
                "event": "tool_result_accepted",
                "tool": state.selected_tool,
            },
        )

        state.current_state = WorkflowState.SYNTHESIZE
        return

    # --------------------------------------------------------
    # Failed result with retries remaining
    # --------------------------------------------------------

    if state.tool_attempts < MAX_TOOL_RETRIES:
        _record_trace(
            state,
            {
                "event": "tool_retry_requested",
                "tool": state.selected_tool,
                "attempt": state.tool_attempts,
                "max_retries": MAX_TOOL_RETRIES,
            },
        )

        state.current_state = WorkflowState.EXECUTE_TOOL
        return

    # --------------------------------------------------------
    # Retry limit reached
    # --------------------------------------------------------

    state.errors.append(
        "Tool execution failed after the maximum "
        "number of attempts."
    )

    _record_trace(
        state,
        {
            "event": "tool_retry_exhausted",
            "tool": state.selected_tool,
            "attempts": state.tool_attempts,
        },
    )

    state.current_state = WorkflowState.SYNTHESIZE

    # --------------------------------------------------------
    # Failed result
    # --------------------------------------------------------

    if state.tool_attempts < MAX_TOOL_RETRIES:
        _record_trace(
            state,
            {
                "event": "tool_retry_requested",
                "tool": state.selected_tool,
                "attempt": state.tool_attempts,
                "max_retries": MAX_TOOL_RETRIES,
            },
        )

        return

    state.errors.append(
        "Tool execution failed after the maximum "
        "number of attempts."
    )

    _record_trace(
        state,
        {
            "event": "tool_retry_exhausted",
            "tool": state.selected_tool,
            "attempts": state.tool_attempts,
        },
    )


# ============================================================
# Synthesize response
# ============================================================


def synthesize_response(
    state: AgentState,
) -> None:
    """
    Convert the available workflow result into a concise response.

    This baseline uses deterministic synthesis rather than another
    unconstrained model call. That keeps the agent auditable and
    makes the Week 9 workflow tests deterministic.
    """

    # --------------------------------------------------------
    # Unsupported request
    # --------------------------------------------------------

    if not state.selected_tool:
        if any(
            "unsupported side effect" in error.lower()
            for error in state.errors
        ):
            state.final_answer = (
                "Iâ€™m sorry, but I canâ€™t perform that "
                "action. The available tools are read-only "
                "and cannot modify, delete, cancel, or "
                "refund records."
            )

        else:
            state.final_answer = (
                "I'm sorry, but I could not safely "
                "process that request."
            )

        _record_trace(
            state,
            {
                "event": "response_synthesized",
                "source": "safe_fallback",
            },
        )

        return

    result = state.tool_result or {}

    success = bool(
        result.get("success", False)
    )
    # --------------------------------------------------------
    # Valid "not found" customer lookup
    # --------------------------------------------------------

    if (
        state.selected_tool == "customer_lookup"
        and result.get("found") is False
    ):
        customer_id = result.get(
            "customer_id",
            "the requested customer",
        )

        state.final_answer = (
            f"Customer {customer_id} was not found."
        )

        _record_trace(
            state,
            {
                "event": "response_synthesized",
                "source": "customer_lookup",
                "reason": "customer_not_found",
            },
        )

        return

    # --------------------------------------------------------
    # Failed tool
    # --------------------------------------------------------

    if not success:
        error = result.get(
            "error",
            "The requested operation could not be completed.",
        )

        state.final_answer = (
            "Iâ€™m sorry, but I could not complete that "
            f"request safely. {error}"
        )

        _record_trace(
            state,
            {
                "event": "response_synthesized",
                "source": "tool_failure",
            },
        )

        return

    # --------------------------------------------------------
    # Customer lookup
    # --------------------------------------------------------

    if state.selected_tool == "customer_lookup":
        customer = result.get(
            "customer"
        )

        if customer:
            first_name = customer.get(
                "first_name",
                "",
            )

            last_name = customer.get(
                "last_name",
                "",
            )

            country = customer.get(
                "country",
                "unknown country",
            )

            status = customer.get(
                "status",
                "unknown status",
            )

            customer_id = customer.get(
                "customer_id",
                state.tool_args.get(
                    "customer_id",
                    "customer",
                ),
            )

            state.final_answer = (
                f"Customer {customer_id} is "
                f"{first_name} {last_name}, "
                f"from {country}, with status "
                f"{status}."
            )

        else:
            state.final_answer = (
                "The customer lookup completed, but "
                "no customer details were returned."
            )

    # --------------------------------------------------------
    # Order status
    # --------------------------------------------------------

    elif state.selected_tool == "order_status":
        order = result.get(
            "order"
        )

        if order:
            order_id = order.get(
                "order_id",
                state.tool_args.get(
                    "order_id",
                    "order",
                ),
            )

            status = order.get(
                "status",
                "unknown",
            )

            state.final_answer = (
                f"Order {order_id} has status "
                f"{status}."
            )

        else:
            state.final_answer = (
                "The order lookup completed, but "
                "no order details were returned."
            )

    # --------------------------------------------------------
    # KPI query
    # --------------------------------------------------------

    elif state.selected_tool == "kpi_query":
        kpi_name = result.get(
            "kpi_name",
            state.tool_args.get(
                "kpi_name",
                "KPI",
            ),
        )

        value = result.get("value")
        unit = result.get("unit")

        if value is None:
            state.final_answer = (
                f"The {kpi_name} was calculated, "
                "but no KPI value was returned."
            )
            return
        if kpi_name == "kpi_summary":
            state.final_answer = (
                "Key business KPIs:\n"
                f"- Total orders: {int(value['total_orders'])}\n"
                f"- Total customers: {int(value['total_customers'])}\n"
                f"- Completed revenue: "
                f"{float(value['completed_revenue']):,.2f} AED\n"
                f"- Average order value: "
                f"{float(value['average_order_value']):,.2f} AED\n"
                f"- Payment success rate: "
                f"{float(value['payment_success_rate']):.2f}%\n"
                f"- Repeat-purchase rate: "
                f"{float(value['repeat_purchase_rate']):.2f}%\n"
                f"- Customer value: "
                f"{float(value['customer_value']):,.2f} AED"
            )
            return

        # ----------------------------------------------------
        # Product rankings
        # ----------------------------------------------------

        if kpi_name == "top_selling_products":
            lines = ["Top-selling products:"]

            for index, product in enumerate(
                value,
                start=1,
            ):
                lines.append(
                    f"{index}. "
                    f"{product['product_name']} — "
                    f"{product['units_sold']} units"
                )

            state.final_answer = "\n".join(lines)
            return

        if kpi_name == "top_product_revenue":
            lines = ["Top products by revenue:"]

            for index, product in enumerate(
                value,
                start=1,
            ):
                lines.append(
                    f"{index}. "
                    f"{product['product_name']} — "
                    f"{product['revenue']:,.2f} AED"
                )

            state.final_answer = "\n".join(lines)
            return

        # ----------------------------------------------------
        # Scalar KPIs
        # ----------------------------------------------------

        if kpi_name in {
            "completed_revenue",
            "average_order_value",
            "customer_value",
        }:
            formatted_value = f"{float(value):,.2f}"
            state.final_answer = (
                f"The {kpi_name.replace('_', ' ')} is "
                f"{formatted_value} AED."
            )
            return

        if kpi_name in {
            "payment_success_rate",
            "repeat_purchase_rate",
        }:
            state.final_answer = (
                f"The {kpi_name.replace('_', ' ')} is "
                f"{float(value):.2f}%."
            )
            return

        if kpi_name == "total_orders":
            state.final_answer = (
                f"The total number of orders is "
                f"{int(value)}."
            )
            return

        if kpi_name == "total_customers":
            state.final_answer = (
                f"The total number of customers is "
                f"{int(value)}."
            )
            return

        state.final_answer = (
            f"The {kpi_name.replace('_', ' ')} is "
            f"{value}."
        )

        value = result.get(
            "value"
        )

        unit = result.get(
            "unit"
        )

        if value is not None:
            if unit:
                state.final_answer = (
                    f"The {kpi_name} is "
                    f"{value} {unit}."
                )

            else:
                state.final_answer = (
                    f"The {kpi_name} is "
                    f"{value}."
                )

        else:
            state.final_answer = (
                f"The {kpi_name} was calculated, "
                "but no KPI value was returned."
            )

    # --------------------------------------------------------
    # Documentation / RAG
    # --------------------------------------------------------

    elif state.selected_tool == "documentation_search":
        answer = result.get(
            "answer"
        )

        if answer:
            state.final_answer = answer

        else:
            state.final_answer = (
                "I found relevant documentation, but "
                "no answer was returned."
            )

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    else:
        state.final_answer = (
            "The request was processed successfully."
        )

    _record_trace(
        state,
        {
            "event": "response_synthesized",
            "source": state.selected_tool,
        },
    )


# ============================================================
# Validate response
# ============================================================


def validate_response(
    state: AgentState,
) -> None:
    """
    Validate the final response before returning it.

    Validation ensures:
    - a response exists
    - the response is a string
    - the response is not empty
    - unsupported actions are not presented as completed
    """

    if not isinstance(
        state.final_answer,
        str,
    ):
        state.errors.append(
            "Final answer is not a string."
        )

        state.final_answer = (
            "Iâ€™m sorry, but I could not safely "
            "generate a response."
        )

    state.final_answer = (
        state.final_answer.strip()
    )

    if not state.final_answer:
        state.errors.append(
            "Final answer is empty."
        )

        state.final_answer = (
            "Iâ€™m sorry, but I could not safely "
            "generate a response."
        )

    # --------------------------------------------------------
    # Safety validation
    # --------------------------------------------------------

    if any(
        "unsupported side effect" in error.lower()
        for error in state.errors
    ):
        unsafe_completion_phrases = [
            "deleted successfully",
            "removed successfully",
            "updated successfully",
            "modified successfully",
            "cancelled successfully",
            "refunded successfully",
        ]

        answer_lower = state.final_answer.lower()

        if any(
            phrase in answer_lower
            for phrase in unsafe_completion_phrases
        ):
            state.final_answer = (
                "Iâ€™m sorry, but I canâ€™t perform that "
                "action. The available tools are read-only."
            )

    _record_trace(
        state,
        {
            "event": "response_validated",
            "valid": bool(
                state.final_answer
            ),
        },
    )


# ============================================================
# Respond
# ============================================================


def respond(
    state: AgentState,
) -> None:
    """
    Mark the workflow as ready to return the response.
    """

    _record_trace(
        state,
        {
            "event": "response_ready",
            "answer": state.final_answer,
        },
    )


# ============================================================
# Main workflow
# ============================================================


def run_agent(
    question: str,
) -> dict[str, Any]:
    """
    Run the complete bounded agent workflow.

    Returns a structured result containing:

        success
        question
        answer
        selected_tool
        tool_args
        tool_result
        step_count
        tool_attempts
        errors
        terminated
        trace
    """

    state = AgentState(
        question=question
    )

    while (
        not state.terminated
        and state.step_count < MAX_STEPS
    ):
        state.step_count += 1

        # ----------------------------------------------------
        # UNDERSTAND
        # ----------------------------------------------------

        if (
            state.current_state
            == WorkflowState.UNDERSTAND
        ):
            try:
                understand_request(
                    state
                )

                state.current_state = (
                    WorkflowState.SELECT_TOOL
                )

            except Exception as exc:
                state.errors.append(
                    f"Request understanding failed: {exc}"
                )

                state.final_answer = (
                    "Iâ€™m sorry, but I could not safely "
                    "understand that request."
                )

                state.current_state = (
                    WorkflowState.RESPOND
                )

        # ----------------------------------------------------
        # SELECT TOOL
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.SELECT_TOOL
        ):
            try:
                select_tool(
                    state
                )

            except Exception as exc:
                state.errors.append(
                    f"Tool selection failed: {exc}"
                )

                state.selected_tool = None
                state.tool_args = {}

                _record_trace(
                    state,
                    {
                        "event": "tool_selection_error",
                        "error": str(exc),
                    },
                )

            if state.selected_tool:
                state.current_state = (
                    WorkflowState.EXECUTE_TOOL
                )

            else:
                state.current_state = (
                    WorkflowState.SYNTHESIZE
                )

        # ----------------------------------------------------
        # EXECUTE TOOL
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.EXECUTE_TOOL
        ):
            execute_tool(
                state
            )

            state.current_state = (
                WorkflowState.EVALUATE_RESULT
            )

        # ----------------------------------------------------
        # EVALUATE RESULT
        # ----------------------------------------------------

        elif (
            state.current_state
            ==
            WorkflowState.EVALUATE_RESULT
        ):
            evaluate_result(
                state
            )

        # ----------------------------------------------------
        # SYNTHESIZE
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.SYNTHESIZE
        ):
            synthesize_response(
                state
            )

            state.current_state = (
                WorkflowState.VALIDATE
            )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.VALIDATE
        ):
            validate_response(
                state
            )

            state.current_state = (
                WorkflowState.RESPOND
            )

        # ----------------------------------------------------
        # RESPOND
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.RESPOND
        ):
            respond(
                state
            )

            state.current_state = (
                WorkflowState.TERMINATE
            )

        # ----------------------------------------------------
        # TERMINATE
        # ----------------------------------------------------

        elif (
            state.current_state
            == WorkflowState.TERMINATE
        ):
            state.terminated = True

            _record_trace(
                state,
                {
                    "event": "workflow_terminated",
                },
            )

    # ========================================================
    # Step limit
    # ========================================================

    if not state.terminated:
        state.errors.append(
            "Workflow step limit reached."
        )

        state.final_answer = (
            "Iâ€™m sorry, but I could not complete "
            "the request within the allowed workflow "
            "step limit."
        )

        state.current_state = (
            WorkflowState.TERMINATE
        )

        state.terminated = True

        _record_trace(
            state,
            {
                "event": "workflow_terminated",
                "reason": "step_limit",
            },
        )

    # ========================================================
    # Success calculation
    # ========================================================

    tool_success = (
        state.selected_tool is None
        or (
            state.tool_result is not None
            and bool(
                state.tool_result.get(
                    "success",
                    False,
                )
            )
        )
    )

    # Unsupported requests are considered safely completed
    # when they terminate without executing a tool.
    safe_unsupported_request = (
        state.selected_tool is None
        and state.terminated
    )

    success = bool(
        state.terminated
        and (
            tool_success
            or safe_unsupported_request
        )
        and bool(
            state.final_answer
        )
    )

    return {
        "success": success,
        "question": state.question,
        "answer": state.final_answer,
        "selected_tool": state.selected_tool,
        "tool_args": state.tool_args,
        "tool_result": state.tool_result,
        "step_count": state.step_count,
        "tool_attempts": state.tool_attempts,
        "errors": state.errors,
        "terminated": state.terminated,
        "trace": state.trace,
    }


# ============================================================
# CLI demonstration
# ============================================================


def _print_result(
    question: str,
    result: dict[str, Any],
) -> None:
    """
    Pretty-print an agent result.
    """

    print()
    print("=" * 70)
    print(
        f"QUESTION: {question}"
    )
    print("=" * 70)

    print(
        f"ANSWER: {result['answer']}"
    )

    print(
        f"TOOL: {result['selected_tool']}"
    )

    print(
        f"STEPS: {result['step_count']}"
    )

    print(
        f"TOOL ATTEMPTS: "
        f"{result['tool_attempts']}"
    )

    print(
        f"TERMINATED: "
        f"{result['terminated']}"
    )

    print(
        f"SUCCESS: "
        f"{result['success']}"
    )

    if result["errors"]:
        print(
            "ERRORS:"
        )

        for error in result["errors"]:
            print(
                f"  - {error}"
            )


def main() -> None:
    """
    Run representative Week 9 workflow examples.
    """

    questions = [
        "What is the status of ORD-00001?",
        "Show me the details for CUST-0001.",
        "What is the completed revenue?",
        "How long do I have to return an item?",
        "Tell me something unsupported.",
        "Delete customer CUST-0001.",
    ]

    for question in questions:
        result = run_agent(
            question
        )

        _print_result(
            question,
            result,
        )


if __name__ == "__main__":
    main()
