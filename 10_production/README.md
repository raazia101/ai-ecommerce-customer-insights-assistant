\# Week 11 — Production Engineering



\## Objective



Week 11 hardens the Week 10 conversational AI application for release.



The focus is on:



\- reliability

\- testing

\- observability

\- security

\- configuration management

\- deployment readiness



The existing AI functionality is intentionally preserved rather than redesigned.



\---



\## Production Architecture



The Week 10 application remains the core system:



User

→ Streamlit UI

→ FastAPI

→ Conversation Service

→ Week 9 Agent Workflow

→ Approved Tool or RAG

→ Response Validation

→ User



Week 11 adds production engineering around this architecture.



\---



\## Refactoring



The application maintains clear boundaries between:



\- Streamlit UI

\- FastAPI API layer

\- conversation/session management

\- Week 9 agent workflow

\- approved tools

\- RAG retrieval

\- data services



Configuration is supplied through environment variables rather than hard-coded secrets.



The API uses typed Pydantic request and response models.



Application logging is enabled for operational visibility.



\---



\## Testing



The project uses layered testing:



\### Unit Tests



Individual functions and components are tested independently.



Examples include:



\- tool validation

\- workflow transitions

\- request validation

\- conversation helpers

\- memory behavior



\### Component Tests



Larger isolated components are tested:



\- agent workflow

\- RAG retrieval

\- conversation service

\- approved tools



\### Integration Tests



The API integration layer is tested through:



\- `/health`

\- `/chat`

\- session clearing

\- validation failures

\- agent integration



\### End-to-End Testing



The complete flow is validated:



User

→ API

→ Conversation Service

→ Agent

→ Tool/RAG

→ Response



\### Security Testing



The project also contains red-team tests covering:



\- prompt injection

\- unauthorized data requests

\- destructive actions

\- arbitrary SQL

\- malformed identifiers

\- nonexistent records

\- unsupported requests

\- cross-session context leakage



\---



\## Observability



The application provides lightweight application-level observability.



\### Logging



The API records:



\- request method

\- endpoint

\- HTTP status

\- request latency

\- application events



\### Tracing



Each chat request receives a trace ID.



Agent traces record:



\- workflow state

\- event

\- selected tool

\- tool arguments

\- tool result

\- retry attempts

\- termination

\- step count



\### Quality Signals



The application can evaluate:



\- task success

\- tool selection

\- groundedness

\- RAG source availability

\- safe refusal behavior

\- multi-turn context correctness



\---



\## Security



Security controls include:



\- environment-based secret configuration

\- Pydantic request validation

\- bounded request sizes

\- bounded tool results

\- allowlisted tools

\- read-only operations

\- prompt-injection defenses

\- generic error responses

\- session isolation

\- dependency auditing



The system does not provide arbitrary:



\- SQL execution

\- Python execution

\- database mutation

\- customer deletion

\- order cancellation

\- refunds



Consequential actions would require an explicit approval mechanism in a future production deployment.



\---



\## Deployment



The Week 11 deployment target uses Docker Compose.



The planned services are:



\- PostgreSQL

\- MongoDB

\- FastAPI

\- Streamlit



PostgreSQL and MongoDB use persistent Docker volumes.



Health checks are configured for the database services.



The API exposes port `8000`.



The Streamlit UI exposes port `8501`.



\---



\## Local Model Service



The RAG system uses the local Ollama/Qwen2.5:3b setup established during the previous weeks.



The model service remains external to the API container during the release-candidate deployment.



The API can communicate with a host Ollama instance through `host.docker.internal`.



\---



\## Known Limitations



The current release candidate has several intentional limitations:



1\. Session state is currently in memory.

2\. Authentication and authorization are not yet implemented.

3\. Centralized metrics and distributed tracing are not yet implemented.

4\. Feedback is not persisted to a production analytics store.

5\. Ollama is treated as an external local model service.

6\. Production-scale model serving is outside the current internship scope.



\---



\## Week 11 Release



Target release:



`v1.2-release-candidate`



Week 11 prepares the application for the final Week 12 capstone delivery, verification and showcase.

