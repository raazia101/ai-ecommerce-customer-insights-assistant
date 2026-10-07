# Agent Decision Guide

## Purpose

This document defines when the agent should use each available
capability.

| Request Type | Action |
|---|---|
| Customer lookup | customer_lookup |
| Order status | order_status |
| KPI/business metric | kpi_query |
| FAQ/policy/documentation | documentation_search |
| Unsupported or unsafe request | safe fallback |

## Customer Lookup

Use when the user asks about a specific customer.

Examples:

- "Show customer CUST-0001."
- "What information do we have for this customer?"
- "Look up CUST-0005."

Required argument:

customer_id

---

## Order Status

Use when the user asks about an order.

Examples:

- "Where is order ORD-0001?"
- "What is the status of my order?"
- "Check ORD-0003."

Required argument:

order_id

---

## KPI Query

Use when the user requests an aggregate business metric.

Examples:

- "What is the average order value?"
- "How many orders were placed?"
- "What is the total revenue?"

The tool must only expose approved KPI definitions.

The agent must not generate arbitrary SQL.

---

## Documentation Search

Use when the question depends on support documentation.

Examples:

- "How long do I have to return an item?"
- "Why was my payment declined?"
- "What payment methods are supported?"
- "What is the refund policy?"

The documentation search tool uses the Week 8 RAG pipeline.

---

## Unsupported Requests

If no available tool can safely answer the request, the agent
must not invent an answer.

It should return a controlled fallback.

Example:

"I don't have an available tool or support document that can answer
that request."

---

## Side Effects

The initial agent is read-only.

Requests involving:

- refunds,
- cancellations,
- account modifications,
- record deletion,
- or other side effects

must not be executed automatically.

Such actions require an explicit approval mechanism.