\# Week 10 Sequence Diagrams



\## E-commerce Customer Insights Assistant



These sequence diagrams describe the main interaction flows between the user interface, API, conversation layer, Week 9 agent, approved tools, and Week 8 RAG pipeline.



\---



\# 1. Standard Chat Request



```text

User

&#x20;â”‚

&#x20;â”‚  Natural-language question

&#x20;â–¼

Streamlit UI

&#x20;â”‚

&#x20;â”‚  POST /chat

&#x20;â–¼

FastAPI

&#x20;â”‚

&#x20;â”‚  Validate request

&#x20;â”‚

&#x20;â–¼

Conversation Layer

&#x20;â”‚

&#x20;â”‚  Understand intent

&#x20;â”‚

&#x20;â–¼

Week 9 Agent

&#x20;â”‚

&#x20;â”‚  Select approved tool

&#x20;â”‚

&#x20;â–¼

Approved Tool

&#x20;â”‚

&#x20;â”‚  Execute read-only operation

&#x20;â”‚

&#x20;â–¼

Database / Analytics

&#x20;â”‚

&#x20;â”‚  Result

&#x20;â–¼

Approved Tool

&#x20;â”‚

&#x20;â”‚  Structured result

&#x20;â–¼

Week 9 Agent

&#x20;â”‚

&#x20;â”‚  Evaluate + synthesize

&#x20;â–¼

Conversation Layer

&#x20;â”‚

&#x20;â”‚  Format response

&#x20;â”‚  Attach sources if applicable

&#x20;â–¼

FastAPI

&#x20;â”‚

&#x20;â”‚  Structured response

&#x20;â–¼

Streamlit UI

&#x20;â”‚

&#x20;â”‚  Display answer

&#x20;â–¼

User
