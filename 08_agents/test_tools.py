"""
Week 9 - Tool Unit Tests

Tests:
    - Customer lookup
    - Order status
    - KPI query
    - Documentation search
    - Input validation
    - Unknown tool handling

The documentation/RAG tool is mocked so these tests do not
depend on Ollama, Chroma, or the embedding model.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


# ============================================================================
# Load tools.py directly
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_PATH = PROJECT_ROOT / "08_agents" / "tools.py"

spec = importlib.util.spec_from_file_location(
    "agent_tools",
    TOOLS_PATH,
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Unable to load tools module from {TOOLS_PATH}"
    )

tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


# ============================================================================
# Customer Lookup Tests
# ============================================================================

def test_customer_lookup_existing_customer():
    result = tools.customer_lookup("CUST-0001")

    assert result["success"] is True
    assert result["tool"] == "customer_lookup"
    assert result["found"] is True
    assert result["customer_id"] == "CUST-0001"
    assert "customer" in result


def test_customer_lookup_case_insensitive():
    result = tools.customer_lookup("cust-0001")

    assert result["success"] is True
    assert result["found"] is True
    assert result["customer_id"] == "CUST-0001"


def test_customer_lookup_missing_customer():
    result = tools.customer_lookup("CUST-9999")

    assert result["success"] is False
    assert result["found"] is False
    assert result["customer_id"] == "CUST-9999"


def test_customer_lookup_invalid_prefix():
    with pytest.raises(ValueError):
        tools.customer_lookup("ORD-0001")


def test_customer_lookup_empty_id():
    with pytest.raises(ValueError):
        tools.customer_lookup("")


# ============================================================================
# Order Status Tests
# ============================================================================

def test_order_status_existing_order():
    result = tools.order_status("ORD-00001")

    assert result["success"] is True
    assert result["tool"] == "order_status"
    assert result["found"] is True
    assert result["order_id"] == "ORD-00001"
    assert "order" in result
    assert "transactions" in result


def test_order_status_case_insensitive():
    result = tools.order_status("ord-00001")

    assert result["success"] is True
    assert result["found"] is True
    assert result["order_id"] == "ORD-00001"


def test_order_status_missing_order():
    result = tools.order_status("ORD-99999")

    assert result["success"] is False
    assert result["found"] is False
    assert result["order_id"] == "ORD-99999"


def test_order_status_invalid_prefix():
    with pytest.raises(ValueError):
        tools.order_status("CUST-0001")


def test_order_status_empty_id():
    with pytest.raises(ValueError):
        tools.order_status("")


# ============================================================================
# KPI Tests
# ============================================================================

@pytest.mark.parametrize(
    "kpi_name",
    [
        "payment_success_rate",
        "completed_revenue",
        "average_order_value",
        "repeat_purchase_rate",
        "customer_value",
    ],
)
def test_kpi_query_approved_kpis(kpi_name):
    result = tools.kpi_query(kpi_name)

    assert result["success"] is True
    assert result["tool"] == "kpi_query"
    assert result["kpi_name"] == kpi_name
    assert "value" in result
    assert "unit" in result
    assert "source" in result


def test_kpi_query_case_insensitive():
    result = tools.kpi_query("AVERAGE_ORDER_VALUE")

    assert result["success"] is True
    assert result["kpi_name"] == "average_order_value"


def test_kpi_query_unsupported_kpi():
    result = tools.kpi_query("customer_profit_margin")

    assert result["success"] is False
    assert result["tool"] == "kpi_query"
    assert "allowed_kpis" in result


def test_kpi_query_does_not_allow_sql():
    result = tools.kpi_query(
        "SELECT * FROM transactions"
    )

    assert result["success"] is False
    assert result["message"] == "Unsupported KPI."


def test_kpi_query_non_string():
    with pytest.raises(ValueError):
        tools.kpi_query(123)


# ============================================================================
# Documentation Search Tests
# ============================================================================

def test_documentation_search_empty_question():
    with pytest.raises(ValueError):
        tools.documentation_search("")


def test_documentation_search_non_string():
    with pytest.raises(ValueError):
        tools.documentation_search(123)


def test_documentation_search_calls_rag_pipeline():
    """
    Mock the Week 8 RAG pipeline so this test verifies the
    agent tool interface without loading embeddings or Ollama.
    """

    fake_result = {
        "answer": "Items can be returned within the allowed return period.",
        "sources": [
            {
                "source": "faq.md",
                "section": "Returns",
            }
        ],
        "retrieved_chunks": [
            {
                "source": "faq.md",
                "section": "Returns",
                "chunk_index": 0,
            }
        ],
    }

    fake_rag_module = type(
        "FakeRagModule",
        (),
        {
            "run_rag": Mock(return_value=fake_result),
        },
    )()

    fake_loader = type(
        "FakeLoader",
        (),
        {
            "exec_module": lambda self, module: None,
        },
    )()

    fake_spec = type(
        "FakeSpec",
        (),
        {
            "loader": fake_loader,
        },
    )()

    with patch(
        "importlib.util.spec_from_file_location",
        return_value=fake_spec,
    ), patch(
        "importlib.util.module_from_spec",
        return_value=fake_rag_module,
    ):
        result = tools.documentation_search(
            "How long do I have to return an item?"
        )

    fake_rag_module.run_rag.assert_called_once_with(
        "How long do I have to return an item?"
    )

    assert result["success"] is True
    assert result["tool"] == "documentation_search"
    assert result["question"] == (
        "How long do I have to return an item?"
    )
    assert result["answer"] == fake_result["answer"]
    assert result["sources"] == fake_result["sources"]
    assert result["retrieved_chunks"] == fake_result["retrieved_chunks"]

# ============================================================================
# Tool Registry Tests
# ============================================================================

def test_list_tools():
    names = tools.list_tools()

    assert names == [
        "customer_lookup",
        "documentation_search",
        "kpi_query",
        "order_status",
    ]


def test_get_tool():
    customer_tool = tools.get_tool("customer_lookup")

    assert customer_tool is tools.customer_lookup


def test_get_unknown_tool():
    with pytest.raises(ValueError):
        tools.get_tool("delete_customer")


# ============================================================================
# Result Bound Tests
# ============================================================================

def test_max_result_rows_is_bounded():
    assert tools.MAX_RESULT_ROWS == 10


def test_query_length_limit_is_bounded():
    assert tools.MAX_QUERY_LENGTH == 200