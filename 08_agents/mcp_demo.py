"""
Week 9 - MCP Demonstration

This module provides a safe local demonstration of the Model Context
Protocol (MCP) concept.

The goal is to demonstrate the architectural idea:

    Agent
      |
      v
    MCP-style tool interface
      |
      +--> Customer lookup
      +--> Order status
      +--> KPI query
      +--> Documentation search

This is intentionally a local educational demonstration. It does not
require an external MCP server or remote service.

The implementation focuses on:
- tool discovery
- typed tool arguments
- controlled tool execution
- structured results
- separation between the agent and tool implementation
- safe handling of invalid tool requests
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from tools import (
    TOOLS,
    customer_lookup,
    documentation_search,
    kpi_query,
    order_status,
)


# ============================================================================
# MCP-style Tool Definition
# ============================================================================

@dataclass(frozen=True)
class MCPTool:
    """
    Local representation of an MCP-style tool.

    A real MCP implementation exposes tools through a standardized protocol.
    For this internship demonstration, we model the important concept:
    the agent discovers tools through a structured interface rather than
    directly depending on implementation details.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]


# ============================================================================
# MCP Tool Registry
# ============================================================================

MCP_TOOLS: dict[str, MCPTool] = {
    "customer_lookup": MCPTool(
        name="customer_lookup",
        description="Look up a customer using a customer ID.",
        input_schema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer identifier such as CUST-0001.",
                }
            },
            "required": ["customer_id"],
        },
        handler=customer_lookup,
    ),
    "order_status": MCPTool(
        name="order_status",
        description="Retrieve order status and transaction information.",
        input_schema={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier such as ORD-00001.",
                }
            },
            "required": ["order_id"],
        },
        handler=order_status,
    ),
    "kpi_query": MCPTool(
        name="kpi_query",
        description="Retrieve an approved business KPI.",
        input_schema={
            "type": "object",
            "properties": {
                "kpi_name": {
                    "type": "string",
                    "description": (
                        "Approved KPI such as completed_revenue or "
                        "average_order_value."
                    ),
                }
            },
            "required": ["kpi_name"],
        },
        handler=kpi_query,
    ),
    "documentation_search": MCPTool(
        name="documentation_search",
        description="Search approved company documentation through RAG.",
        input_schema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Question to search in company documentation.",
                }
            },
            "required": ["question"],
        },
        handler=documentation_search,
    ),
}


# ============================================================================
# MCP Discovery
# ============================================================================

def list_mcp_tools() -> list[dict[str, Any]]:
    """
    Return tool metadata that an agent could discover.

    The implementation details of each handler are intentionally hidden.
    """

    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        }
        for tool in MCP_TOOLS.values()
    ]


# ============================================================================
# MCP Tool Lookup
# ============================================================================

def get_mcp_tool(name: str) -> MCPTool | None:
    """
    Retrieve a registered MCP-style tool by name.
    """

    if not isinstance(name, str):
        return None

    return MCP_TOOLS.get(name)


# ============================================================================
# MCP Tool Invocation
# ============================================================================

def call_mcp_tool(
    name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Invoke an MCP-style tool using structured arguments.

    Safety properties:
    - tool name must exist in the registry
    - arguments must be a dictionary
    - only registered handlers can execute
    - exceptions are converted into structured errors
    """

    if not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "error": "Invalid tool name.",
        }

    if not isinstance(arguments, dict):
        return {
            "success": False,
            "error": "Tool arguments must be an object.",
        }

    tool = get_mcp_tool(name)

    if tool is None:
        return {
            "success": False,
            "error": f"Unknown MCP tool: {name}",
        }

    try:
        result = tool.handler(**arguments)

    except TypeError as exc:
        return {
            "success": False,
            "error": f"Invalid arguments for {name}: {exc}",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Tool execution failed: {exc}",
        }

    return {
        "success": True,
        "tool": name,
        "result": result,
    }


# ============================================================================
# MCP Request / Response Demonstration
# ============================================================================

def build_tool_request(
    name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a simple MCP-style tool request object.
    """

    return {
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments,
        },
    }


def run_demo() -> None:
    """
    Demonstrate MCP-style discovery and tool execution.
    """

    print("=" * 70)
    print("MCP-STYLE TOOL DEMONSTRATION")
    print("=" * 70)

    # ------------------------------------------------------------------------
    # 1. Tool discovery
    # ------------------------------------------------------------------------

    print("\n1. DISCOVERED TOOLS")

    discovered_tools = list_mcp_tools()

    for tool in discovered_tools:
        print(f"- {tool['name']}: {tool['description']}")

    # ------------------------------------------------------------------------
    # 2. Show structured schema
    # ------------------------------------------------------------------------

    print("\n2. TOOL SCHEMA")

    customer_tool = get_mcp_tool("customer_lookup")

    if customer_tool is not None:
        print(
            json.dumps(
                {
                    "name": customer_tool.name,
                    "description": customer_tool.description,
                    "input_schema": customer_tool.input_schema,
                },
                indent=2,
            )
        )

    # ------------------------------------------------------------------------
    # 3. Build an MCP-style request
    # ------------------------------------------------------------------------

    print("\n3. TOOL REQUEST")

    request = build_tool_request(
        "customer_lookup",
        {
            "customer_id": "CUST-0001",
        },
    )

    print(json.dumps(request, indent=2))

    # ------------------------------------------------------------------------
    # 4. Execute through the MCP-style interface
    # ------------------------------------------------------------------------

    print("\n4. TOOL RESPONSE")

    response = call_mcp_tool(
        request["params"]["name"],
        request["params"]["arguments"],
    )

    print(json.dumps(response, indent=2, default=str))

    # ------------------------------------------------------------------------
    # 5. Invalid tool demonstration
    # ------------------------------------------------------------------------

    print("\n5. INVALID TOOL REQUEST")

    invalid_response = call_mcp_tool(
        "delete_customer",
        {
            "customer_id": "CUST-0001",
        },
    )

    print(
        json.dumps(
            invalid_response,
            indent=2,
        )
    )

    # ------------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------------

    print("\n6. MCP CONCEPT")

    print(
        "The agent does not need to know how each tool is implemented."
    )

    print(
        "It discovers available tools through structured metadata,"
    )

    print(
        "selects a tool, supplies typed arguments, and receives a"
    )

    print(
        "structured result through the tool interface."
    )

    print("\nDemo complete.")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    run_demo()