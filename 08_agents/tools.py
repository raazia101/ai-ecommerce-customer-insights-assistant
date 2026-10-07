"""
Week 9 - Agent Tools

Typed, validated, read-only tools exposed to the agent controller.

Tools:
    1. customer_lookup
    2. order_status
    3. kpi_query
    4. documentation_search

Design principles:
    - Read-only operations
    - Explicit typed arguments
    - Input validation
    - Bounded results
    - Compact tool responses
    - No arbitrary SQL
    - No side effects
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CURATED_DIR = PROJECT_ROOT / "data" / "curated"


# ---------------------------------------------------------------------------
# Tool limits
# ---------------------------------------------------------------------------

MAX_RESULT_ROWS = 10
MAX_QUERY_LENGTH = 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_identifier(
    value: str,
    prefix: str,
    field_name: str,
) -> str:
    """
    Validate a business identifier such as CUST-0001 or ORD-0001.
    """

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    value = value.strip().upper()

    if not value:
        raise ValueError(f"{field_name} cannot be empty.")

    if len(value) > 50:
        raise ValueError(f"{field_name} is too long.")

    if not value.startswith(prefix):
        raise ValueError(
            f"{field_name} must start with '{prefix}'."
        )

    return value


def _load_parquet(filename: str) -> pd.DataFrame:
    """
    Load a curated parquet dataset.
    """

    path = CURATED_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Curated dataset not found: {path}"
        )

    return pd.read_parquet(path)


def _records_to_compact_dict(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert pandas/numpy scalar values into normal Python values
    so tool results remain JSON-friendly.
    """

    compact = []

    for record in records[:MAX_RESULT_ROWS]:
        cleaned = {}

        for key, value in record.items():
            if pd.isna(value):
                cleaned[key] = None
            elif hasattr(value, "item"):
                cleaned[key] = value.item()
            elif hasattr(value, "isoformat"):
                cleaned[key] = value.isoformat()
            else:
                cleaned[key] = value

        compact.append(cleaned)

    return compact


# ---------------------------------------------------------------------------
# Tool 1 - Customer Lookup
# ---------------------------------------------------------------------------

def customer_lookup(customer_id: str) -> dict[str, Any]:
    """
    Look up a customer by customer ID.

    Args:
        customer_id: Customer business identifier, e.g. CUST-0001.

    Returns:
        Compact structured customer information.
    """

    customer_id = _validate_identifier(
        customer_id,
        prefix="CUST-",
        field_name="customer_id",
    )

    customers = _load_parquet("customers.parquet")

    matches = customers[
        customers["customer_id"].astype(str).str.upper()
        == customer_id
    ]

    if matches.empty:
        return {
            "success": False,
            "tool": "customer_lookup",
            "customer_id": customer_id,
            "found": False,
            "message": "Customer not found.",
        }

    record = matches.iloc[0].to_dict()

    return {
        "success": True,
        "tool": "customer_lookup",
        "customer_id": customer_id,
        "found": True,
        "customer": _records_to_compact_dict([record])[0],
    }


# ---------------------------------------------------------------------------
# Tool 2 - Order Status
# ---------------------------------------------------------------------------

def order_status(order_id: str) -> dict[str, Any]:
    """
    Look up order status and related payment information.

    Args:
        order_id: Order business identifier, e.g. ORD-0001.

    Returns:
        Compact order and transaction information.
    """

    order_id = _validate_identifier(
        order_id,
        prefix="ORD-",
        field_name="order_id",
    )

    orders = _load_parquet("orders.parquet")
    transactions = _load_parquet("transactions.parquet")

    order_matches = orders[
        orders["order_id"].astype(str).str.upper()
        == order_id
    ]

    if order_matches.empty:
        return {
            "success": False,
            "tool": "order_status",
            "order_id": order_id,
            "found": False,
            "message": "Order not found.",
        }

    order = order_matches.iloc[0].to_dict()

    transaction_matches = transactions[
        transactions["order_id"].astype(str).str.upper()
        == order_id
    ]

    transaction_records = _records_to_compact_dict(
        transaction_matches
        .head(MAX_RESULT_ROWS)
        .to_dict(orient="records")
    )

    return {
        "success": True,
        "tool": "order_status",
        "order_id": order_id,
        "found": True,
        "order": _records_to_compact_dict([order])[0],
        "transactions": transaction_records,
        "transaction_count": len(transaction_records),
    }


# ---------------------------------------------------------------------------
# Tool 3 - KPI Query
# ---------------------------------------------------------------------------

APPROVED_KPIS = {
    "payment_success_rate": "payment_success_rate_pct",
    "completed_revenue": "completed_revenue",
    "average_order_value": "average_order_value",
    "repeat_purchase_rate": "repeat_purchase_rate_pct",
    "customer_value": "customer_value",
}


def kpi_query(kpi_name: str) -> dict[str, Any]:
    """
    Calculate one approved business KPI.

    Arbitrary SQL and arbitrary expressions are deliberately not supported.

    Args:
        kpi_name:
            One of the approved KPI names.

    Returns:
        Structured KPI result.
    """

    if not isinstance(kpi_name, str):
        raise ValueError("kpi_name must be a string.")

    kpi_name = kpi_name.strip().lower()

    if len(kpi_name) > MAX_QUERY_LENGTH:
        raise ValueError("kpi_name is too long.")

    if kpi_name not in APPROVED_KPIS:
        return {
            "success": False,
            "tool": "kpi_query",
            "kpi_name": kpi_name,
            "allowed_kpis": sorted(APPROVED_KPIS.keys()),
            "message": "Unsupported KPI.",
        }

    # Reuse the existing Week 4 KPI implementation.
    from importlib.util import module_from_spec, spec_from_file_location

    kpis_path = PROJECT_ROOT / "05_analytics" / "kpis.py"

    spec = spec_from_file_location(
        "project_kpis",
        kpis_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError("Unable to load the existing KPI module.")

    kpis_module = module_from_spec(spec)
    spec.loader.exec_module(kpis_module)

    transactions = kpis_module.load_transactions(PROJECT_ROOT)
    all_kpis = kpis_module.calculate_all_kpis(transactions)

    result_key = APPROVED_KPIS[kpi_name]
    value = all_kpis[result_key]

    if hasattr(value, "item"):
        value = value.item()

    return {
        "success": True,
        "tool": "kpi_query",
        "kpi_name": kpi_name,
        "value": value,
        "unit": (
            "percentage"
            if kpi_name.endswith("rate")
            else "AED"
        ),
        "source": "05_analytics/kpis.py",
    }


# ---------------------------------------------------------------------------
# Tool 4 - Documentation Search
# ---------------------------------------------------------------------------

def documentation_search(
    question: str,
) -> dict[str, Any]:
    """
    Search the Week 8 RAG knowledge base.

    This tool deliberately delegates documentation retrieval and
    grounded generation to the existing Week 8 RAG pipeline.

    Args:
        question: Natural-language documentation/policy question.

    Returns:
        Structured RAG result.
    """

    if not isinstance(question, str):
        raise ValueError("question must be a string.")

    question = question.strip()

    if not question:
        raise ValueError("question cannot be empty.")

    if len(question) > MAX_QUERY_LENGTH:
        raise ValueError(
            f"question cannot exceed {MAX_QUERY_LENGTH} characters."
        )

    from importlib.util import module_from_spec, spec_from_file_location

    rag_path = PROJECT_ROOT / "07_llm_rag" / "rag_pipeline.py"

    spec = spec_from_file_location(
        "project_rag_pipeline",
        rag_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Unable to load the Week 8 RAG pipeline."
        )

    rag_module = module_from_spec(spec)
    spec.loader.exec_module(rag_module)

    result = rag_module.run_rag(question)

    return {
        "success": True,
        "tool": "documentation_search",
        "question": question,
        "answer": result.get("answer"),
        "sources": result.get("sources", []),
        "retrieved_chunks": result.get(
            "retrieved_chunks",
            [],
        ),
    }


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS = {
    "customer_lookup": customer_lookup,
    "order_status": order_status,
    "kpi_query": kpi_query,
    "documentation_search": documentation_search,
}


def get_tool(name: str):
    """
    Return a registered tool by name.
    """

    if name not in TOOLS:
        raise ValueError(
            f"Unknown tool '{name}'. "
            f"Available tools: {sorted(TOOLS)}"
        )

    return TOOLS[name]


def list_tools() -> list[str]:
    """
    Return the names of all available tools.
    """

    return sorted(TOOLS.keys())