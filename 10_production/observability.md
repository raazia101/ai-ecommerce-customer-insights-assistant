\# Week 11 Observability



\## Purpose



Observability allows the behavior of the application to be inspected during development, testing and deployment.



The Week 10 system already provides useful agent-level tracing. Week 11 extends this with application-level operational visibility.



\---



\## Logging



The API records basic request information including:



\- HTTP method

\- endpoint

\- HTTP status

\- request latency

\- application events



Logs are intended to help diagnose operational failures without exposing sensitive implementation details.



\---



\## Trace IDs



Each chat request receives a unique trace ID.



The trace ID allows a request to be associated with its downstream processing.



Conceptually:



User Request

→ API Request

→ Conversation Service

→ Agent Workflow

→ Tool/RAG

→ Response



\---



\## Agent Tracing



The bounded agent workflow records:



\- current workflow state

\- workflow event

\- selected tool

\- tool arguments

\- tool result

\- tool attempt number

\- step count

\- termination



The workflow therefore provides visibility into how a request progressed through:



UNDERSTAND

→ SELECT\_TOOL

→ EXECUTE\_TOOL

→ EVALUATE\_RESULT

→ SYNTHESIZE

→ VALIDATE

→ RESPOND

→ TERMINATE



\---



\## Metrics and Operational Signals



Important signals include:



\### API



\- request count

\- HTTP errors

\- response latency



\### Agent



\- workflow step count

\- tool attempts

\- retries

\- termination status

\- tool errors



\### RAG



\- retrieval results

\- source availability

\- retrieval latency

\- generation latency



\### AI Quality



\- task success

\- groundedness

\- source availability

\- safe refusal behavior

\- tool selection correctness

\- multi-turn context correctness



\---



\## Error Observability



Internal exceptions are logged for debugging while user-facing responses remain generic.



This prevents implementation details such as:



\- database errors

\- file paths

\- dependency errors

\- stack traces



from being returned directly to users.



\---



\## Current Scope



The current implementation provides lightweight application-level observability.



A production-scale deployment could additionally introduce:



\- OpenTelemetry

\- Prometheus

\- Grafana

\- centralized log aggregation

\- distributed tracing

\- alerting

\- persistent metrics storage



These are considered future production improvements rather than mandatory internship scope.

