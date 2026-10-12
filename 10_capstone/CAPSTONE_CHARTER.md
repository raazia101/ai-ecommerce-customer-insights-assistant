# Capstone Charter
## AI-Powered E-commerce Customer Insights Assistant

**Project:** AI-Powered E-commerce Customer Insights Assistant  
**Internship:** INTERNSHIP-SAAL  
**Capstone Version:** v1.2 ? v1.3  
**Planning Phase:** Week 12 — Day 1  
**Repository:** `intern-project`

---

# 1. Project Overview

The AI-Powered E-commerce Customer Insights Assistant is an integrated data and AI application designed to provide conversational access to e-commerce customer, order, KPI, and documentation information.

The project combines data engineering, analytics, machine learning, large language models, retrieval-augmented generation (RAG), bounded agent workflows, API development, and production-oriented deployment into a single application.

The capstone represents the culmination of the internship work completed across Weeks 1–11 and focuses on validating, documenting, testing, and presenting the complete system during Week 12.

---

# 2. Problem Statement

E-commerce information is distributed across structured business data, analytical datasets, machine-learning outputs, and internal documentation.

Users who need customer, order, KPI, or policy information may otherwise need to manually query databases, inspect dashboards, or search through documentation.

The goal of this project is to provide a controlled conversational assistant that allows users to obtain relevant e-commerce information through a single application interface.

The assistant combines structured data access, analytics, machine learning, RAG, and bounded agent capabilities while maintaining explicit boundaries around the actions the AI system is permitted to perform.

---

# 3. Target Users

The primary target users are:

- E-commerce and business analysts
- Customer-support and operations users
- Business stakeholders who need accessible e-commerce insights

The system is designed to reduce the effort required to retrieve supported business information from underlying data and documentation sources.

---

# 4. Core Objectives

The capstone objectives are to:

1. Provide conversational access to supported e-commerce information.
2. Integrate structured e-commerce data with an AI application layer.
3. Demonstrate an evaluated machine-learning use case.
4. Provide retrieval-augmented generation over project documentation.
5. Use a bounded and controlled agent workflow.
6. Expose the application through a FastAPI service.
7. Provide a user-facing Streamlit interface.
8. Run the integrated application using Docker-based production infrastructure.
9. Provide operational observability through health checks, logging, request tracing, and latency measurement.
10. Demonstrate reproducibility, testing, documentation, and deployment readiness.

---

# 5. Primary Use Cases

## 5.1 Customer Lookup

The assistant can use the bounded `customer_lookup` capability to retrieve supported customer information.

## 5.2 Order Status

The assistant can use the bounded `order_status` capability to retrieve order-status information.

Example validated request:

> What is the status of ORD-00001?

Validated response:

> Order ORD-00001 has status pending.

## 5.3 KPI Queries

The assistant can use the bounded `kpi_query` capability to retrieve supported business metrics and e-commerce KPIs.

## 5.4 Documentation Search

The assistant can use `documentation_search` and the RAG pipeline to retrieve relevant information from indexed project documentation.

---

# 6. Agent Safety Boundary

The agent operates using explicitly approved, read-only capabilities:

- `customer_lookup`
- `order_status`
- `kpi_query`
- `documentation_search`

The capstone does not provide unrestricted access to databases or external systems.

The current agent scope is intentionally read-only. It does not perform side effects such as modifying customer records, modifying orders, processing payments, or executing uncontrolled external actions.

This bounded design provides a clear safety and engineering boundary around the AI workflow.

---

# 7. Application Architecture

The final application follows this high-level architecture:

```text
                         USER
                           |
                           v
                  +------------------+
                  |   Streamlit UI   |
                  |    Port 8501     |
                  +--------+---------+
                           |
                           v
                  +------------------+
                  |     FastAPI      |
                  |    Port 8000     |
                  +--------+---------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
        ConversationService     Request
                 |              Observability
                 v
          Agent Adapter
                 |
                 v
          Bounded Agent
                 |
       +---------+---------+----------------+
       |                   |                |
       v                   v                v
customer_lookup       order_status      kpi_query
       |                   |                |
       +-------------------+----------------+
                           |
                           v
                      PostgreSQL

                 documentation_search
                           |
                           v
                      RAG Pipeline
                           |
                           v
                      Vector Store
