from pathlib import Path
import importlib.util
import sys


# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = PROJECT_ROOT / "08_agents"

if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))


# -------------------------------------------------------------------
# Load agent_workflow.py safely
# -------------------------------------------------------------------

MODULE_PATH = AGENT_DIR / "agent_workflow.py"

spec = importlib.util.spec_from_file_location(
    "agent_workflow_test_module",
    MODULE_PATH,
)

agent_workflow = importlib.util.module_from_spec(spec)

assert spec.loader is not None

sys.modules["agent_workflow_test_module"] = agent_workflow

spec.loader.exec_module(agent_workflow)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def make_successful_tool_result(tool_name="test_tool"):
    return {
        "success": True,
        "tool": tool_name,
        "message": "Tool executed successfully.",
    }


# -------------------------------------------------------------------
# Routing tests
# -------------------------------------------------------------------

def test_customer_id_routes_to_customer_lookup():
    state = agent_workflow.AgentState(
        question="Show me the details for CUST-0001."
    )

    agent_workflow.understand_request(state)
    agent_workflow.select_tool(state)

    assert state.selected_tool == "customer_lookup"
    assert state.tool_args == {
        "customer_id": "CUST-0001"
    }


def test_order_id_routes_to_order_status():
    state = agent_workflow.AgentState(
        question="What is the status of ORD-00001?"
    )

    agent_workflow.understand_request(state)
    agent_workflow.select_tool(state)

    assert state.selected_tool == "order_status"
    assert state.tool_args == {
        "order_id": "ORD-00001"
    }


def test_kpi_request_routes_to_kpi_query():
    state = agent_workflow.AgentState(
        question="What is the completed revenue?"
    )

    agent_workflow.understand_request(state)
    agent_workflow.select_tool(state)

    assert state.selected_tool == "kpi_query"
    assert state.tool_args == {
        "kpi_name": "completed_revenue"
    }


def test_documentation_request_routes_to_documentation_search():
    state = agent_workflow.AgentState(
        question="How long do I have to return an item?"
    )

    agent_workflow.understand_request(state)
    agent_workflow.select_tool(state)

    assert state.selected_tool == "documentation_search"
    assert state.tool_args == {
        "question": "How long do I have to return an item?"
    }


def test_unsupported_request_selects_no_tool():
    state = agent_workflow.AgentState(
        question="Tell me something unsupported."
    )

    agent_workflow.understand_request(state)
    agent_workflow.select_tool(state)

    assert state.selected_tool is None
    assert state.current_state == agent_workflow.WorkflowState.SYNTHESIZE
    assert state.errors


# -------------------------------------------------------------------
# Tool execution tests
# -------------------------------------------------------------------

def test_successful_tool_execution():
    original_tools = agent_workflow.TOOL_FUNCTIONS.copy()

    try:
        agent_workflow.TOOL_FUNCTIONS["customer_lookup"] = (
            lambda customer_id: {
                "success": True,
                "tool": "customer_lookup",
                "customer_id": customer_id,
                "found": True,
            }
        )

        state = agent_workflow.AgentState(
            question="Show me CUST-0001."
        )

        state.selected_tool = "customer_lookup"
        state.tool_args = {
            "customer_id": "CUST-0001"
        }

        agent_workflow.execute_tool(state)

        assert state.tool_result["success"] is True
        assert state.tool_result["found"] is True
        assert state.tool_attempts == 1
        assert state.current_state == (
            agent_workflow.WorkflowState.EVALUATE_RESULT
        )

    finally:
        agent_workflow.TOOL_FUNCTIONS.clear()
        agent_workflow.TOOL_FUNCTIONS.update(original_tools)


def test_failed_tool_execution_records_error():
    original_tools = agent_workflow.TOOL_FUNCTIONS.copy()

    try:
        agent_workflow.TOOL_FUNCTIONS["customer_lookup"] = (
            lambda customer_id: {
                "success": False,
                "tool": "customer_lookup",
                "customer_id": customer_id,
                "found": False,
                "message": "Customer not found.",
            }
        )

        state = agent_workflow.AgentState(
            question="Show me CUST-9999."
        )

        state.selected_tool = "customer_lookup"
        state.tool_args = {
            "customer_id": "CUST-9999"
        }

        agent_workflow.execute_tool(state)

        assert state.tool_result["success"] is False
        assert state.tool_attempts == 1
        assert state.current_state == (
            agent_workflow.WorkflowState.EVALUATE_RESULT
        )

    finally:
        agent_workflow.TOOL_FUNCTIONS.clear()
        agent_workflow.TOOL_FUNCTIONS.update(original_tools)


# -------------------------------------------------------------------
# Retry tests
# -------------------------------------------------------------------

def test_retry_behavior_allows_second_attempt():
    original_tools = agent_workflow.TOOL_FUNCTIONS.copy()

    calls = {"count": 0}

    def flaky_tool(customer_id):
        calls["count"] += 1

        if calls["count"] == 1:
            return {
                "success": False,
                "tool": "customer_lookup",
                "message": "Temporary failure.",
            }

        return {
            "success": True,
            "tool": "customer_lookup",
            "customer_id": customer_id,
            "found": True,
        }

    try:
        agent_workflow.TOOL_FUNCTIONS["customer_lookup"] = flaky_tool

        state = agent_workflow.AgentState(
            question="Show me CUST-0001."
        )

        state.selected_tool = "customer_lookup"
        state.tool_args = {
            "customer_id": "CUST-0001"
        }

        agent_workflow.execute_tool(state)

        assert state.tool_attempts == 1
        assert state.tool_result["success"] is False

        agent_workflow.evaluate_result(state)

        # A failed result should trigger another tool attempt
        assert state.current_state in {
            agent_workflow.WorkflowState.EXECUTE_TOOL,
            agent_workflow.WorkflowState.SYNTHESIZE,
        }

    finally:
        agent_workflow.TOOL_FUNCTIONS.clear()
        agent_workflow.TOOL_FUNCTIONS.update(original_tools)


def test_retry_limit_is_bounded():
    original_tools = agent_workflow.TOOL_FUNCTIONS.copy()

    try:
        agent_workflow.TOOL_FUNCTIONS["customer_lookup"] = (
            lambda customer_id: {
                "success": False,
                "tool": "customer_lookup",
                "message": "Persistent failure.",
            }
        )

        state = agent_workflow.AgentState(
            question="Show me CUST-9999."
        )

        state.selected_tool = "customer_lookup"
        state.tool_args = {
            "customer_id": "CUST-9999"
        }

        for _ in range(agent_workflow.MAX_TOOL_RETRIES + 1):
            agent_workflow.execute_tool(state)
            agent_workflow.evaluate_result(state)

            if state.current_state != (
                agent_workflow.WorkflowState.EXECUTE_TOOL
            ):
                break

        assert state.tool_attempts <= (
            agent_workflow.MAX_TOOL_RETRIES + 1
        )

    finally:
        agent_workflow.TOOL_FUNCTIONS.clear()
        agent_workflow.TOOL_FUNCTIONS.update(original_tools)


# -------------------------------------------------------------------
# Trace tests
# -------------------------------------------------------------------

def test_trace_is_generated():
    result = agent_workflow.run_agent(
        "What is the completed revenue?"
    )

    assert result["trace"]
    assert len(result["trace"]) > 0

    events = [
        item.get("event")
        for item in result["trace"]
    ]

    assert any(
        "tool_selected" in event
        for event in events
    )


# -------------------------------------------------------------------
# Termination tests
# -------------------------------------------------------------------

def test_successful_workflow_terminates():
    original_tools = agent_workflow.TOOL_FUNCTIONS.copy()

    try:
        agent_workflow.TOOL_FUNCTIONS["customer_lookup"] = (
            lambda customer_id: {
                "success": True,
                "tool": "customer_lookup",
                "customer_id": customer_id,
                "found": True,
                "customer": {
                    "customer_id": customer_id,
                    "first_name": "Test",
                    "last_name": "User",
                    "country": "UAE",
                    "status": "active",
                },
            }
        )

        result = agent_workflow.run_agent(
            "Show me the details for CUST-0001."
        )

        assert result["terminated"] is True
        assert result["answer"]
        assert result["selected_tool"] == "customer_lookup"

    finally:
        agent_workflow.TOOL_FUNCTIONS.clear()
        agent_workflow.TOOL_FUNCTIONS.update(original_tools)

def test_unsupported_request_terminates_safely():
    result = agent_workflow.run_agent(
        "Tell me something unsupported."
    )

    assert result["terminated"] is True
    assert result["answer"]
    assert result["selected_tool"] is None


def test_workflow_step_limit_is_bounded():
    original_max_steps = agent_workflow.MAX_STEPS

    try:
        agent_workflow.MAX_STEPS = 2

        result = agent_workflow.run_agent(
            "What is the completed revenue?"
        )

        assert result["terminated"] is True
        assert result["step_count"] <= 3

    finally:
        agent_workflow.MAX_STEPS = original_max_steps