# E-commerce Customer Insights Assistant

## Overview

The E-commerce Customer Insights Assistant is a controlled conversational AI application developed as the capstone stage of the internship project.

The application integrates the components developed throughout the project:

- Data engineering
- PostgreSQL data warehouse
- Analytics and KPI layer
- Machine learning
- LLM foundations
- Retrieval-Augmented Generation (RAG)
- Stateful agent workflows
- Memory
- FastAPI
- Streamlit
- Safety and red-team testing

The assistant provides a conversational interface for customer, order, KPI, and documentation-related questions.

The system is intentionally bounded and does not provide unrestricted autonomous database access or destructive operations.

---

# Architecture

The final application follows this architecture:

```text
                         USER
                           |
                           v
                    STREAMLIT UI
                           |
                           v
                     FASTAPI API
                           |
                           v
                 CONVERSATION LAYER
                           |
                           v
               WEEK 9 CONTROLLED AGENT
                           |
              +------------+-------------+
              |            |             |
              v            v             v
        APPROVED TOOLS    RAG       SESSION CONTEXT
              |            |
              v            v
        POSTGRESQL     DOCUMENTATION
