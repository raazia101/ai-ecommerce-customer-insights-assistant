# Capstone Documentation
>> ## AI-Powered E-commerce Customer Insights Assistant
>>
>> **Internship:** INTERNSHIP-SAAL
>> **Release:** v1.3 Capstone
>> **Previous Release:** v1.2 Release Candidate
>> **Repository:** `intern-project`
>>
>> ---
>>
>> # 1. System Overview
>>
>> The AI-Powered E-commerce Customer Insights Assistant is an integrated application combining:
>>
>> - Data engineering
>> - Analytics
>> - Machine learning
>> - Large language models
>> - Retrieval-augmented generation (RAG)
>> - Bounded agent workflows
>> - FastAPI
>> - Streamlit
>> - PostgreSQL
>> - MongoDB
>> - Ollama
>> - Docker
>>
>> The application provides a conversational interface for supported e-commerce customer, order, KPI, and documentation queries.
>>
>> ---
>>
>> # 2. Architecture
>>
>> ```text
>>                          USER
>>                            |
>>                            v
>>                   +----------------+
>>                   |  Streamlit UI  |
>>                   |    :8501       |
>>                   +-------+--------+
>>                           |
>>                           v
>>                   +----------------+
>>                   |    FastAPI     |
>>                   |    :8000       |
>>                   +-------+--------+
>>                           |
>>                           v
>>                  ConversationService
>>                           |
>>                           v
>>                     Agent Adapter
>>                           |
>>                           v
>>                    Bounded Agent
>>                           |
>>              +------------+-------------+
>>              |            |             |
>>              v            v             v
>>       customer_lookup order_status  kpi_query
>>              |            |             |
>>              +------------+-------------+
>>                           |
>>                           v
>>                      PostgreSQL
>>
>>              documentation_search
>>                           |
>>                           v
>>                      RAG Pipeline
>>                           |
>>                           v
>>                      Vector Store```

The final application brings together the work completed across the internship, from data engineering and analytics through machine learning, LLM development, RAG, agent workflows, API development, testing, and production deployment.

---

# 2. Project Objectives

The final capstone was designed to demonstrate the ability to build an end-to-end AI-powered business application rather than an isolated machine-learning or LLM experiment.

The main objectives were:

1. Build a complete data-to-AI application.
2. Integrate structured business data with AI capabilities.
3. Provide a conversational interface for supported business questions.
4. Implement a bounded and deterministic agent workflow.
5. Integrate retrieval-augmented generation for documentation queries.
6. Expose the application through a production-style FastAPI service.
7. Provide a Streamlit user interface.
8. Package the application and supporting services with Docker Compose.
9. Validate the application through automated tests.
10. Document deployment, usage, architecture, limitations, and troubleshooting.
11. Produce a final release candidate suitable for demonstration and evaluation.

---

# 3. Problem Statement

E-commerce systems generate large amounts of customer, order, product, transaction, and event data.

Although this information can be queried using databases and analytical tools, business users may not always have the technical knowledge required to directly interact with the underlying data systems.

The project addresses this problem by providing a conversational assistant capable of answering supported business questions through a controlled AI workflow.

Instead of requiring a user to manually construct SQL queries, navigate multiple systems, or search documentation independently, the assistant provides a single conversational interface.

The application combines:

- Structured database queries
- Business analytics
- Customer information retrieval
- Order-status retrieval
- KPI queries
- Documentation retrieval
- Agent-based orchestration
- API services
- User-facing UI

The architecture also deliberately limits agent capabilities so that the system remains predictable and easier to test and operate.

---

# 4. Target Users

The primary target users are:

- Business analysts
- E-commerce operations teams
- Customer-support teams
- Product or business stakeholders
- Data analysts
- Technical evaluators
- Internship/project reviewers

The application is particularly useful for users who need quick access to supported business information without directly interacting with the underlying database or application infrastructure.

---

# 5. Primary Use Cases

The assistant supports several categories of questions.

## 5.1 Order Status

Example:

```
What is the status of ORD-00001?
```

The agent uses the `order_status` tool to retrieve the relevant order information.

Verified response:

```
Order ORD-00001 has status pending.
```

---

## 5.2 Customer Lookup

The assistant can use the `customer_lookup` capability for supported customer-related queries.

This provides a controlled interface between conversational requests and structured customer information.

---

## 5.3 Business KPI Queries

The `kpi_query` tool provides access to supported business-level KPI queries.

The agent does not receive unrestricted database access. Instead, it interacts through the explicitly defined tool interface.

---

## 5.4 Documentation Search

Documentation-related questions can be routed through the `documentation_search` capability.

This connects the agent to the project's retrieval-augmented generation pipeline.

---

# 6. Agent Safety Boundary

A central design principle of the application is bounded agent execution.

The agent is not provided with unrestricted access to:

- The operating system
- Arbitrary files
- Arbitrary shell commands
- Arbitrary database operations
- Unapproved external services
- Unrestricted write operations

The approved capabilities are:

```
customer_lookup
order_status
kpi_query
documentation_search
```

These tools provide controlled interfaces for the operations that the assistant is expected to perform.

This architecture improves:

- Predictability
- Security
- Testability
- Debuggability
- Reproducibility
- Operational control

The design also makes it easier to reason about which actions an AI component can and cannot perform.

---

# 7. Application Architecture

The final application follows the architecture below:

```
                         USER
                           |
                           v
                  +----------------+
                  |  Streamlit UI  |
                  |     :8501      |
                  +-------+--------+
                          |
                          v
                  +----------------+
                  |    FastAPI     |
                  |     :8000      |
                  +-------+--------+
                          |
                          v
                 ConversationService
                          |
                          v
                    Agent Adapter
                          |
                          v
                    Bounded Agent
                          |
             +------------+-------------+
             |            |             |
             v            v             v
      customer_lookup  order_status  kpi_query
             |            |             |
             +------------+-------------+
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
```

The Streamlit layer provides the user-facing conversational interface.

The FastAPI layer provides the application API.

The `ConversationService` manages the conversational interaction.

The agent adapter connects the API/application layer to the Week 9 bounded agent workflow.

The bounded agent selects approved tools based on the user request.

Structured business queries are handled through the PostgreSQL-backed tools.

Documentation queries are handled through the RAG pipeline and vector store.

---

# 8. Production Services

The production environment is managed using Docker Compose.

The main services are:

| Service    | Purpose                   | Port  |
| ---------- | ------------------------- | ----- |
| API        | FastAPI application       | 8000  |
| UI         | Streamlit application     | 8501  |
| PostgreSQL | Structured business data  | 5433  |
| MongoDB    | Document-oriented storage | 27017 |
| Ollama     | Local LLM runtime         | 11434 |

The production stack uses Docker containers so that the main application services can be started and managed together.

The API service is exposed on host port `8000`.

The Streamlit UI is exposed on host port `8501`.

PostgreSQL is exposed on host port `5433` while using port `5432` inside the Docker network.

MongoDB is exposed on port `27017`.

Ollama is exposed on port `11434`.

---

# 9. Production Startup

The production environment can be started from the repository root using:

```
docker compose -f docker-compose.production.yml up -d --build
```

The running services can then be checked with:

```
docker compose -f docker-compose.production.yml ps
```

The expected production stack contains:

```
intern-capstone-api
intern-capstone-mongodb
intern-capstone-ollama
intern-capstone-postgres
intern-capstone-ui
```

The API container includes a health check that verifies whether the FastAPI application is reachable.

---

# 10. Production Service Verification

The production environment was successfully inspected using:

```
docker compose -f docker-compose.production.yml ps
```

The verified service state included:

```
intern-capstone-api        Up ... (healthy)
intern-capstone-mongodb    Up ... (healthy)
intern-capstone-ollama     Up ...
intern-capstone-postgres   Up ... (healthy)
intern-capstone-ui         Up ...
```

The API service was therefore confirmed to be running and healthy.

The PostgreSQL and MongoDB services were also reported healthy.

The Streamlit UI was running and exposed through port `8501`.

---

# 11. API Health Check

The FastAPI application exposes a health endpoint:

```
GET /health
```

It can be tested with:

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

The verified response was:

```
status
------
ok
```

This confirms that the FastAPI service was reachable from the host machine.

The health endpoint is also used by the Docker container health-check configuration.

---

# 12. API Chat Endpoint

The primary conversational endpoint is:

```
POST /chat
```

The endpoint accepts a session identifier and user message.

Example:

```
Invoke-RestMethod -Method POST `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"session_id":"week12-final-test","message":"What is the status of ORD-00001?"}'
```

A verified successful response was:

```
session_id : week12-final-test
trace_id   : ab537fde-bc4d-4884-b422-76f7b674dcf4
response   : Order ORD-00001 has status pending.
sources    : {}
tool_used  : order_status
status     : success
```

This demonstrates that the API successfully processed the request, selected the appropriate agent tool, queried the underlying business data, and returned a response.

---

# 13. API Response Structure

The chat endpoint provides several useful response fields.

## session_id

Identifies the conversation session.

## trace_id

Provides an identifier that can be used to correlate the request with application execution and debugging information.

## response

Contains the assistant's final answer.

## sources

Contains available source information when applicable.

## tool_used

Indicates the tool selected during the request.

## status

Indicates whether the request completed successfully.

Example:

```
tool_used : order_status
status     : success
```

This structure provides more observability than returning only the generated text.

---

# 14. Conversation Management

The application supports session-based conversations.

A client supplies a session identifier together with a message.

Example request:

```
{
  "session_id": "example-session",
  "message": "What is the status of ORD-00001?"
}
```

The conversation service maintains the context associated with the session.

The application also provides conversation-clearing functionality so that sessions can be reset when required.

---

# 15. Streamlit User Interface

The Streamlit application is exposed at:

```
http://127.0.0.1:8501
```

The UI provides a conversational interface over the FastAPI backend.

The UI was tested using:

```
What is the status of ORD-00001?
```

The verified response displayed by the application was:

```
Order ORD-00001 has status pending.
```

This confirms the primary user-facing flow:

```
Streamlit
   |
   v
FastAPI
   |
   v
Conversation Service
   |
   v
Agent
   |
   v
order_status
   |
   v
PostgreSQL
   |
   v
Response
```

---

# 16. Agent Capabilities

The bounded agent has access to four approved capabilities.

## 16.1 customer_lookup

Retrieves supported customer information.

The tool provides a controlled interface for customer-related queries.

---

## 16.2 order_status

Retrieves the status of a supported order.

Example:

```
What is the status of ORD-00001?
```

Verified response:

```
Order ORD-00001 has status pending.
```

---

## 16.3 kpi_query

Provides supported business KPI queries.

This tool allows the agent to access predefined business metrics without exposing unrestricted database operations.

---

## 16.4 documentation_search

Provides access to project documentation through the RAG pipeline.

This allows the assistant to retrieve relevant information from indexed documentation rather than relying only on the model's internal knowledge.

---

# 17. RAG Pipeline

The project includes a retrieval-augmented generation pipeline for documentation-oriented questions.

The general workflow is:

```
Documentation
      |
      v
Document Loading
      |
      v
Chunking
      |
      v
Embedding Generation
      |
      v
Vector Store
      |
      v
Similarity Retrieval
      |
      v
Retrieved Context
      |
      v
LLM / Agent
```

The Week 8 implementation indexed documentation including:

```
faq.md
policies.md
```

The implementation produced:

```
Documents found: 2
Chunks created: 14
Embedding shape: (14, 384)
Retrieval evaluation queries: 8
```

The embedding model used was:

```
all-MiniLM-L6-v2
```

The vector store was implemented using ChromaDB.

The `documentation_search` tool provides the agent with access to this retrieval capability.

---

# 18. RAG Verification Status

The RAG infrastructure was implemented and evaluated during the earlier RAG development phase.

However, the final Week 12 release should distinguish between:

1. RAG infrastructure existing and functioning,
2. retrieval evaluation having been performed,
3. final end-to-end source-grounded behavior being explicitly verified.

The first two were established during the earlier implementation.

The final Week 12 release should not claim that every RAG acceptance criterion has been freshly revalidated unless the corresponding final verification test has been executed.

In particular, the following should be explicitly verified before final release if required by the evaluator:

- Source-grounded answers
- Citation/source reporting
- Insufficient-evidence behavior
- Appropriate refusal or decline when evidence is inadequate

---

# 19. Machine Learning Component

The project includes a customer repeat-purchase prediction workflow.

The ML workflow includes:

```
Customer Data
      |
      v
Feature Engineering
      |
      v
Feature Validation
      |
      v
Model Training
      |
      v
Cross-Validation
      |
      v
Model Artifact
      |
      v
Prediction API
```

The baseline model used logistic regression.

The earlier ML training workflow reported:

```
Dataset shape: (84, 24)
Feature matrix shape: (84, 21)
Numerical features: 19
Categorical features: 2
```

The target distribution was:

```
repeat_purchase = 0 : 51
repeat_purchase = 1 : 33
```

A 5-fold stratified cross-validation process was used for the baseline evaluation.

The model was also exposed through an API workflow during the earlier implementation.

---

# 20. ML Prediction Verification

The model-serving workflow was previously tested using a sample customer.

The verified example used:

```
customer_id: CUST-0001
prediction: 1
probability: 0.6057741052033203
```

The model artifact was associated with:

```
model_version: week5-logistic-regression-v1
```

The ML component therefore forms the predictive layer of the larger application architecture.

---

# 21. Data Layer

The project uses PostgreSQL as the primary structured data store.

The warehouse/mart layer includes:

```
mart.dim_customer
mart.dim_order
mart.dim_product
mart.fact_order_items
```

The source tables include:

```
customers
order_items
orders
products
transactions
```

The mart layer provides a structured foundation for downstream analytics and AI workflows.

---

# 22. Curated Data

The project contains curated Parquet datasets including:

```
customers.parquet
events.parquet
ml_customer_features.parquet
ml_predictions.parquet
orders.parquet
order_items.parquet
products.parquet
transactions.parquet
```

These datasets support analytical workflows, feature generation, machine-learning processing, and downstream application functionality.

---

# 23. Data Engineering and Analytics

The earlier stages of the project established the data engineering foundation required for the capstone.

The overall data flow can be represented as:

```
Raw Data
   |
   v
Validation
   |
   v
Curated Data
   |
   v
Warehouse / Mart
   |
   +--------------------+
   |                    |
   v                    v
Analytics              ML
   |                    |
   +----------+---------+
              |
              v
        AI Application
```

The project therefore does not treat the LLM or agent as an isolated component.

Instead, the final application is built on top of the structured data, analytics, ML, retrieval, and application layers developed throughout the internship.

---

# 24. Observability and Traceability

The API returns a `trace_id` for successful chat requests.

Example:

```
trace_id : ab537fde-bc4d-4884-b422-76f7b674dcf4
```

The response also exposes:

```
tool_used
status
response
sources
```

This provides useful information for debugging and operational investigation.

A request can therefore be traced from:

```
User Request
     |
     v
API
     |
     v
ConversationService
     |
     v
Agent
     |
     v
Tool
     |
     v
Data Source
     |
     v
Response
```

The trace identifier provides a useful correlation point for this request lifecycle.

---

# 25. Automated Testing

The Week 12 application test suite was executed using:

```
python -m pytest 09_capstone\tests --cov=09_capstone --cov-report=term-missing -q
```

The verified result was:

```
7 passed
```

The coverage report showed:

```
Name                                    Stmts   Miss  Cover
---------------------------------------------------------------------
09_capstone\api\_08_agents_adapter.py      45      7    84%
09_capstone\api\__init__.py                 0      0   100%
09_capstone\api\conversation.py           101      7    93%
09_capstone\api\main.py                    40      4    90%
09_capstone\api\models.py                  17      0   100%
09_capstone\tests\__init__.py               0      0   100%
09_capstone\tests\test_api.py              55      1    98%
---------------------------------------------------------------------
TOTAL                                     258     19    93%
```

The final result was:

```
7 passed, 1 warning
93% total application coverage
```

The warning was a deprecation warning related to the Starlette test client and the AnyIO blocking portal API.

---

# 26. API Failure-Path Verification

An invalid API request was intentionally tested to confirm request validation.

The following request omitted the required `message` field:

```
Invoke-RestMethod -Method POST `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"session_id":"week12-invalid-test"}'
```

The API rejected the request.

The validation response identified:

```
type: missing
loc: ["body","message"]
msg: Field required
```

This confirms that malformed input is rejected through API validation rather than being passed into the agent workflow.

---

# 27. End-to-End Validation

The primary happy path was successfully verified from the user interface through the backend and database.

The validated path was:

```
User
 |
 v
Streamlit UI
 |
 v
FastAPI
 |
 v
ConversationService
 |
 v
Agent Adapter
 |
 v
Bounded Agent
 |
 v
order_status
 |
 v
PostgreSQL
 |
 v
Response
```

The test question was:

```
What is the status of ORD-00001?
```

The final response was:

```
Order ORD-00001 has status pending.
```

The API response additionally contained a session ID, trace ID, tool name, and success status.

This represents the primary end-to-end happy path for the final application.

---

# 28. Failure Handling

The project includes validation and failure handling at several levels.

## API Validation

Missing required fields are rejected by the API validation layer.

## Agent Boundaries

The agent can only access approved tools.

## Tool-Level Execution

Business operations are performed through dedicated tool functions rather than arbitrary model-generated operations.

## Application Errors

The API exposes status information to distinguish successful execution from tool or application errors.

## Health Checks

The API provides a health endpoint and Docker health-check configuration.

---

# 29. Environment Configuration

The production application uses environment variables for service configuration.

Important configuration variables include:

```
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
OLLAMA_BASE_URL
API_URL
```

Inside the Docker network, the API connects to PostgreSQL through the PostgreSQL service name.

The production configuration uses:

```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

The Streamlit application can use:

```
API_URL
```

to locate the FastAPI backend.

Environment-specific secrets must remain outside source control.

---

# 30. Security Considerations

The application follows several security-oriented design principles.

## Secrets

Secrets and credentials should be stored in environment configuration rather than committed to Git.

The `.env` file must not be committed.

## Bounded Agent

The AI agent is restricted to explicitly approved tools.

## API Validation

FastAPI/Pydantic request validation prevents malformed requests from being processed as valid application requests.

## Database Access

Database operations are exposed through controlled application tools rather than unrestricted model-generated SQL.

## Side Effects

The approved agent tools are read-oriented capabilities.

This reduces the risk of an AI-generated request producing unintended external side effects.

---

# 31. Dependency and Security Review

A previous dependency audit identified known vulnerabilities in several installed packages.

The `pip-audit` run reported:

```
21 known vulnerabilities in 8 packages
```

The findings included packages such as:

- ChromaDB
- JupyterLab
- multidict

These findings should be treated as a known security-review item for a production deployment beyond the internship environment.

The project should not claim that all dependency vulnerabilities have been resolved unless an updated dependency audit confirms that.

---

# 32. Troubleshooting

## 32.1 Check Running Services

Use:

```
docker compose -f docker-compose.production.yml ps
```

---

## 32.2 Check API Logs

Use:

```
docker compose -f docker-compose.production.yml logs api
```

For continuously updating logs:

```
docker compose -f docker-compose.production.yml logs -f api
```

---

## 32.3 Check UI Logs

Use:

```
docker compose -f docker-compose.production.yml logs ui
```

---

## 32.4 Check PostgreSQL Logs

Use:

```
docker compose -f docker-compose.production.yml logs postgres
```

---

## 32.5 Check MongoDB Logs

Use:

```
docker compose -f docker-compose.production.yml logs mongodb
```

---

## 32.6 Check Ollama Logs

Use:

```
docker compose -f docker-compose.production.yml logs ollama
```

---

## 32.7 Test API Health

Use:

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected:

```
status
------
ok
```

---

## 32.8 Test the Chat Endpoint

Use:

```
Invoke-RestMethod -Method POST `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"session_id":"debug-session","message":"What is the status of ORD-00001?"}'
```

---

## 32.9 Restart the Production Stack

If services need to be restarted:

```
docker compose -f docker-compose.production.yml restart
```

If the containers need to be rebuilt:

```
docker compose -f docker-compose.production.yml up -d --build
```

---

# 33. Known Limitations

The following limitations should be explicitly acknowledged in the final release documentation.

## 33.1 RAG Final Verification

The RAG infrastructure and retrieval evaluation were implemented during the earlier RAG phase.

However, the final Week 12 release should explicitly verify source-grounded answers and insufficient-evidence behavior before claiming those acceptance criteria as fully validated.

---

## 33.2 Data Pipeline Verification

The project contains the data engineering and curated-data layers, but the complete raw-to-curated pipeline should be explicitly rerun and verified for repeatability and idempotent behavior if required by the final evaluator.

---

## 33.3 ML Scorecard

The machine-learning workflow and model-serving functionality were implemented and tested earlier.

A final release scorecard containing the required model quality metrics should be included if the evaluator requires a consolidated Week 12 ML evidence artifact.

---

## 33.4 Performance

Formal production latency measurements were not established as part of the currently verified Week 12 evidence.

If required, latency should be measured for:

- API request handling
- Agent execution
- Database queries
- RAG retrieval
- End-to-end response time

---

## 33.5 Dependency Vulnerabilities

The previous `pip-audit` run reported known vulnerabilities in installed dependencies.

These should be reviewed before treating the application as production-ready beyond the controlled internship demonstration environment.

---

# 34. Demo Narrative

The recommended demonstration should follow a simple end-to-end story.

## Step 1 — Introduce the Problem

Explain that e-commerce data is distributed across structured data, analytics, ML, documentation, and application systems.

The project brings these components together behind a conversational assistant.

---

## Step 2 — Explain the Architecture

Show:

```
Data
 |
 v
Analytics / ML
 |
 v
RAG
 |
 v
Bounded Agent
 |
 v
FastAPI
 |
 v
Streamlit
```

Explain that the agent is intentionally bounded to approved tools.

---

## Step 3 — Show Production Services

Run:

```
docker compose -f docker-compose.production.yml ps
```

Explain the purpose of:

- API
- UI
- PostgreSQL
- MongoDB
- Ollama

---

## Step 4 — Demonstrate API Health

Run:

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

Show:

```
status
------
ok
```

---

## Step 5 — Demonstrate a Business Query

Ask:

```
What is the status of ORD-00001?
```

Show:

```
Order ORD-00001 has status pending.
```

Explain that the bounded agent selected `order_status`.

---

## Step 6 — Demonstrate the Streamlit UI

Open:

```
http://127.0.0.1:8501
```

Submit:

```
What is the status of ORD-00001?
```

Show the returned answer.

---

## Step 7 — Explain the AI Architecture

Explain that the project includes:

- Machine learning
- LLM foundations
- RAG
- Agent workflows
- API integration
- Production deployment

---

## Step 8 — Explain Testing

Show:

```
7 passed
93% application coverage
```

Explain that the project also includes an invalid-request test demonstrating API validation.

---

# 35. Interview Talking Points

The project demonstrates experience across the complete AI application lifecycle.

## Data Engineering

Key discussion points:

- PostgreSQL warehouse design
- dimensional structures
- fact tables
- curated datasets
- data validation
- analytical data preparation

---

## Analytics

Key discussion points:

- exploratory data analysis
- business metrics
- customer and order analysis
- KPI-oriented data access

---

## Machine Learning

Key discussion points:

- feature engineering
- feature validation
- logistic regression
- stratified cross-validation
- model artifacts
- prediction serving

---

## LLM Engineering

Key discussion points:

- prompt engineering
- structured output
- LLM application design
- evaluation

---

## Retrieval-Augmented Generation

Key discussion points:

- document loading
- chunking
- embeddings
- vector stores
- similarity retrieval
- retrieval evaluation
- documentation search

---

## Agent Engineering

Key discussion points:

- bounded tools
- deterministic workflow
- tool validation
- controlled execution
- failure handling

---

## Application Engineering

Key discussion points:

- FastAPI
- Pydantic validation
- Streamlit
- conversation sessions
- API integration
- error handling

---

## Production Engineering

Key discussion points:

- Docker
- Docker Compose
- service dependencies
- health checks
- environment configuration
- containerized application deployment

---

## Testing

Key discussion points:

- pytest
- API tests
- application tests
- integration testing
- coverage
- happy-path verification
- failure-path verification

---

# 36. Final Release Checklist

## Scope

- Capstone scope defined
- Architecture documented
- Primary user workflow identified
- Agent safety boundary documented

## Integration

- Docker services verified
- API health verified
- API chat happy path verified
- Streamlit happy path verified
- Agent tool execution verified
- PostgreSQL-backed order lookup verified

## Testing

- Automated tests executed
- 7 tests passed
- 93% application coverage recorded
- Invalid API input rejected correctly
- Final RAG source-grounding verification
- Final insufficient-evidence RAG verification
- Final data-quality verification
- Final ML scorecard verification

## Documentation

- Capstone charter created
- Capstone documentation created
- Architecture documented
- Production startup documented
- API usage documented
- Troubleshooting documented
- Known limitations documented
- Demo narrative documented
- README finalized
- Final documentation review

## Security

- Environment-variable configuration documented
- Agent tool boundaries documented
- API validation verified
- Final secret/repository review
- Dependency vulnerability review

## Release

- Final repository review
- Generated/local files reviewed
- Secrets confirmed absent from Git
- Final working tree reviewed
- Final commit created
- `v1.3-capstone` tag created

---

# 37. Capstone Status

The AI-Powered E-commerce Customer Insights Assistant has reached the final capstone and release-preparation stage.

The main production application has been integrated and the primary end-to-end conversational workflow has been successfully verified.

The verified production path is:

```
Streamlit UI
     |
     v
FastAPI
     |
     v
ConversationService
     |
     v
Agent Adapter
     |
     v
Bounded Agent
     |
     v
order_status
     |
     v
PostgreSQL
     |
     v
Successful Response
```

The verified test query:

```
What is the status of ORD-00001?
```

returned:

```
Order ORD-00001 has status pending.
```

The production API also returned a trace ID and tool identifier, providing additional observability.

The automated application test suite produced:

```
7 passed
93% total application coverage
```

The invalid API request test also confirmed that required request fields are validated correctly.

The remaining work for the final release consists primarily of:

1. Final RAG verification
2. Final repository review
3. README finalization
4. Final documentation review
5. Demo preparation
6. Final Git commit
7. Creation of the `v1.3-capstone` release tag

These steps represent the final release, showcase, and career-review phase of the internship project.

---

# 38. Final Release Goal

The final goal of Week 12 is to leave the repository in a reproducible, documented, tested, and demonstrable state.

The intended final state is:

```
Data Engineering
       |
       v
Analytics
       |
       v
Machine Learning
       |
       v
LLM
       |
       v
RAG
       |
       v
Bounded Agent
       |
       v
FastAPI
       |
       v
Streamlit
       |
       v
Docker Production Stack
       |
       v
Final Capstone Release
```

The project demonstrates the complete progression from raw data and analytical infrastructure to an integrated AI application.

The final release should preserve reproducibility, bounded AI behavior, automated testing, operational visibility, clear documentation, and a demonstrable end-to-end workflow.

---

# 39. Conclusion

The internship project progressed from foundational data engineering through analytics, machine learning, LLM development, retrieval-augmented generation, agent workflows, API development, and production engineering.

The final capstone integrates these components into a single AI-powered E-commerce Customer Insights Assistant.

The application demonstrates:

- Structured data engineering
- Analytical workflows
- Machine-learning prediction
- LLM integration
- Retrieval-augmented generation
- Bounded agent execution
- FastAPI application development
- Streamlit interface development
- PostgreSQL integration
- Docker-based deployment
- Automated testing
- API validation
- Observability
- Technical documentation

The project is now positioned for the final Week 12 release and showcase process.

The final release objective is not simply to demonstrate that the application works, but to demonstrate that the application can be understood, tested, reproduced, operated, and evaluated by another person.

---

# 40. Final Handoff

A reviewer taking over the repository should begin with:

```
cd C:\Users\raazi\Documents\intern-project
```

Activate the existing environment if working outside Docker:

```
.\.venv\Scripts\Activate.ps1
```

Start the production environment:

```
docker compose -f docker-compose.production.yml up -d --build
```

Verify the services:

```
docker compose -f docker-compose.production.yml ps
```

Verify the API:

```
Invoke-RestMethod http://127.0.0.1:8000/health
```

Run the automated tests:

```
python -m pytest 09_capstone\tests --cov=09_capstone --cov-report=term-missing -q
```

Open the application:

```
http://127.0.0.1:8501
```

Test the primary workflow:

```
What is the status of ORD-00001?
```

Expected response:

```
Order ORD-00001 has status pending.
```

This provides a concise verification path for a reviewer to confirm that the final application is operational.