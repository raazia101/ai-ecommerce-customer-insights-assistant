# E-commerce Customer Insights Assistant
## Final Demo Script

## 1. Project Overview

The E-commerce Customer Insights Assistant is a conversational AI application that combines:

- PostgreSQL data warehouse
- Analytics and KPI layer
- Machine learning
- RAG-based documentation retrieval
- A bounded stateful agent workflow
- FastAPI backend
- Streamlit chat interface
- Safety and red-team validation

The system answers customer, order, KPI, and documentation-related questions while remaining bounded, validated, and read-only.

---

## 2. Final Architecture

User
â†“
Streamlit UI
â†“
FastAPI Chat API
â†“
Conversation Layer
â†“
Week 9 Controlled Agent
â†“
Approved Tools / Week 8 RAG
â†“
PostgreSQL / Documentation

Approved tools:

- customer_lookup
- order_status
- kpi_query
- documentation_search

---

## 3. Demo Setup

Start FastAPI:

```powershell
python -m uvicorn 09_capstone.api.main:app --reload
