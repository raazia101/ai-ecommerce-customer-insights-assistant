\# Week 10 â€” Application Architecture



\## 1. Purpose



This document defines the architecture for the Week 10 Conversational AI Application.



Week 10 integrates the existing Week 8 RAG system and Week 9 controlled agent workflow into a full-stack conversational application.



The architecture adds:



\- conversation management

\- FastAPI

\- session handling

\- structured API responses

\- trace IDs

\- feedback

\- Streamlit UI

\- source presentation

\- conversation history

\- clear-chat behavior

\- integration testing

\- red-team testing



\---



\# 2. High-Level Architecture



```text

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚                USER                  â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;                   â”‚

&#x20;                   â–¼

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚            STREAMLIT UI              â”‚

â”‚                                      â”‚

â”‚  Chat                               â”‚

â”‚  Conversation History               â”‚

â”‚  Sources                            â”‚

â”‚  Feedback                           â”‚

â”‚  Clear Chat                         â”‚

â”‚  Loading / Error States             â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;                   â”‚ HTTP

&#x20;                   â–¼

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚              FASTAPI                 â”‚

â”‚                                      â”‚

â”‚  /health                             â”‚

â”‚  /chat                               â”‚

â”‚  /feedback                           â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;                   â”‚

&#x20;                   â–¼

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚        CONVERSATION LAYER            â”‚

â”‚                                      â”‚

â”‚  Session Management                  â”‚

â”‚  Turn Handling                       â”‚

â”‚  Context Management                  â”‚

â”‚  Response Contract                   â”‚

â”‚  Trace ID                            â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;                   â”‚

&#x20;                   â–¼

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚            WEEK 9 AGENT              â”‚

â”‚                                      â”‚

â”‚  Understand                          â”‚

â”‚  Select Tool                        â”‚

â”‚  Execute                            â”‚

â”‚  Evaluate                           â”‚

â”‚  Retry                              â”‚

â”‚  Synthesize                         â”‚

â”‚  Validate                           â”‚

â”‚  Respond                            â”‚

â”‚  Terminate                          â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;              â”‚               â”‚

&#x20;              â–¼               â–¼

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

â”‚ APPROVED TOOLS      â”‚  â”‚ WEEK 8 RAG          â”‚

â”‚                     â”‚  â”‚                     â”‚

â”‚ customer\_lookup     â”‚  â”‚ Retrieval           â”‚

â”‚ order\_status        â”‚  â”‚ Embeddings          â”‚

â”‚ kpi\_query           â”‚  â”‚ Chroma              â”‚

â”‚ documentation\_searchâ”‚  â”‚ Evidence            â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚ Grounded Response   â”‚

&#x20;                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
