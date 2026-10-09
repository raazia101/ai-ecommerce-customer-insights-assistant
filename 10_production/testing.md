\# Week 11 Testing



\## Testing Strategy



The application uses a layered testing strategy to reduce the risk of regressions while preparing the system for deployment.



\---



\## Unit Testing



Unit tests validate individual functions and components.



Examples:



\- tool argument validation

\- workflow state transitions

\- Pydantic request validation

\- conversation helper functions

\- memory behavior

\- response validation



\---



\## Component Testing



Component tests validate larger application components independently.



Components include:



\- deterministic agent workflow

\- approved tools

\- RAG retrieval

\- conversation service

\- session management



\---



\## Integration Testing



Integration tests validate interactions between application layers.



The FastAPI integration tests cover:



\- `GET /health`

\- `POST /chat`

\- `DELETE /chat/{session\_id}`

\- successful order queries

\- clarification requests

\- unsupported/destructive requests

\- multi-turn context

\- invalid request validation



\---



\## End-to-End Testing



The intended end-to-end path is:



User

→ Streamlit

→ FastAPI

→ Conversation Service

→ Week 9 Agent

→ Approved Tool or RAG

→ Response Validation

→ Streamlit



The Week 10 application already established this flow and Week 11 preserves it as the production smoke-test path.



\---



\## Security and Red-Team Testing



Security testing covers:



\- direct prompt injection

\- injection embedded in legitimate requests

\- system prompt extraction

\- unauthorized database requests

\- arbitrary SQL

\- destructive operations

\- excessive data requests

\- malformed customer/order identifiers

\- nonexistent records

\- unsupported capabilities

\- cross-session context leakage



The Week 10 red-team suite achieved 15/15 successful cases.



\---



\## Regression Testing



The Week 9 regression suite is retained.



The Week 10 API tests are retained.



The red-team suite is retained.



This ensures production hardening does not remove previously validated behavior.



\---



\## Coverage



Coverage is measured using `pytest-cov`.



Command:



```powershell

pytest --cov=08\_agents --cov=09\_capstone --cov-report=term-missing

