\# Week 10 â€” Conversation Specification



\## 1. Purpose



The purpose of the Week 10 conversational application is to expose the capabilities developed during Weeks 8 and 9 through a usable conversational interface.



The application combines:



\- Week 8 Retrieval-Augmented Generation (RAG)

\- Week 9 controlled agent workflows

\- Week 9 approved read-only tools

\- Week 9 session memory

\- Week 9 durable memory

\- conversation/session handling

\- FastAPI backend integration

\- Streamlit user interface

\- source/citation presentation

\- user feedback

\- trace identifiers

\- safety and fallback behavior



The application is designed as a controlled conversational AI system rather than an unrestricted autonomous agent.



The existing Week 9 agent remains the execution and decision layer. Week 10 adds the application and conversation layer around it.



\---



\# 2. Product Goal



The product goal is to allow a user to interact with the E-commerce Customer Insights Assistant through natural-language conversation.



The user should be able to ask questions involving:



1\. Customer information

2\. Order status

3\. Business KPIs

4\. E-commerce documentation and policies

5\. Multi-turn clarification

6\. Follow-up questions

7\. Requests that require safe refusal or fallback



The application should return responses that are:



\- relevant

\- grounded where external knowledge is required

\- traceable

\- bounded by approved capabilities

\- safe

\- understandable

\- appropriate to the available evidence



\---



\# 3. Existing System Being Integrated



Week 10 builds on the completed Week 8 and Week 9 systems.



\## Week 8



Week 8 provides the RAG capability.



The RAG system includes:



\- document loading

\- document chunking

\- embeddings

\- Chroma vector storage

\- retrieval

\- hybrid retrieval

\- evidence gating

\- context construction

\- grounded generation

\- source information

\- insufficient-evidence handling



The primary purpose of the Week 8 layer is knowledge retrieval and grounded answering.



\---



\## Week 9



Week 9 provides the controlled agent layer.



The approved tools are:



\- `customer\_lookup`

\- `order\_status`

\- `kpi\_query`

\- `documentation\_search`



The agent workflow includes:



\- request understanding

\- tool selection

\- tool execution

\- result evaluation

\- bounded retries

\- synthesis

\- validation

\- response

\- termination

\- tracing

\- safety rejection



The workflow is intentionally controlled and read-only.



It does not perform destructive operations such as:



\- delete

\- remove

\- modify

\- change

\- update

\- edit

\- cancel

\- refund



Week 9 also provides:



\- `SessionMemory`

\- `DurableMemory`

\- memory validation

\- memory classification

\- safety controls

\- evaluation infrastructure



\---



\# 4. Conversation Layer



Week 10 introduces a conversation layer above the Week 9 agent.



The conversation layer is responsible for managing the interaction between the user and the underlying agent.



Conceptually:



User

&#x20;   â†“

Conversation Layer

&#x20;   â†“

Week 9 Agent

&#x20;   â†“

Approved Tool / RAG

&#x20;   â†“

Result

&#x20;   â†“

Conversation Layer

&#x20;   â†“

User



The conversation layer should not replace the Week 9 agent.



Instead, it provides the application-facing boundary around the agent.



\---



\# 5. Supported Conversation Intents



The application supports the following primary intents.



\## 5.1 Customer Lookup



Purpose:



Retrieve information about a specific customer.



Example:



User:

"Show me information about customer CUST-0001."



Expected behavior:



1\. Identify the customer lookup intent.

2\. Validate the customer identifier.

3\. Call `customer\_lookup`.

4\. Evaluate the returned result.

5\. Produce a concise response.

6\. Return the response through the application layer.



\---



\## 5.2 Order Status



Purpose:



Retrieve the status or available information for a specific order.



Example:



User:

"What is the status of ORD-000123?"



Expected behavior:



1\. Identify the order-status intent.

2\. Validate the order identifier.

3\. Call `order\_status`.

4\. Evaluate the result.

5\. Produce a response.



\---



\## 5.3 KPI Query



Purpose:



Answer supported business KPI questions.



Examples:



"What is the average order value?"



"What is our repeat purchase rate?"



"What is the payment success rate?"



Expected behavior:



1\. Identify the KPI intent.

2\. Map the request to an approved KPI.

3\. Call `kpi\_query`.

4\. Evaluate the result.

5\. Present the KPI clearly.



Only approved KPI mappings may be used.



\---



\## 5.4 Documentation Search



Purpose:



Answer questions requiring information from the project's documentation and policy knowledge base.



Example:



"How long do customers have to return an item?"



Expected behavior:



1\. Identify the documentation-search intent.

2\. Call `documentation\_search`.

3\. Retrieve relevant evidence through the Week 8 RAG system.

4\. Check whether sufficient evidence exists.

5\. Generate a grounded response.

6\. Preserve source information for presentation to the user.



\---



\## 5.5 Unsupported or Unsafe Request



The application must recognize requests that are outside its approved capabilities.



Examples:



"Cancel my order."



"Refund this customer."



"Delete this customer."



"Modify the order."



These operations are not available through the Week 9 approved tool registry.



Expected behavior:



1\. Recognize that the requested operation is unsupported.

2\. Do not attempt arbitrary execution.

3\. Do not invent a successful result.

4\. Return a safe explanation.



\---



\# 6. Turn-Taking



The system must support a conversational turn structure.



A basic interaction is:



User

&#x20;   â†“

Assistant

&#x20;   â†“

User

&#x20;   â†“

Assistant



Each user message represents a new conversational turn.



The application must retain sufficient session context to interpret appropriate follow-up messages.



\---



\# 7. Multi-Turn Conversation



The system must support follow-up questions where the previous turn provides relevant context.



Example:



User:

"Show me the status of ORD-000123."



Assistant:

"The order is currently ..."



User:

"When was it placed?"



The second question should be interpreted using the previous conversational context when sufficient information is available.



The system should not unnecessarily ask the user to repeat information that is already available in the current session.



\---



\# 8. Clarification Behavior



The system must ask for clarification when required information is missing or ambiguous.



Example:



User:

"Show me the order."



The system should not guess an order.



Expected response:



"Sure â€” which order ID would you like me to check?"



The user can then provide:



"ORD-000123"



The next turn should use that information.



\---



\# 9. Missing Entity Handling



Required identifiers include:



\- customer IDs for customer lookup

\- order IDs for order lookup



Expected identifier formats include:



Customer:

`CUST-...`



Order:

`ORD-...`



If the required identifier is missing, the application should request it.



If the identifier is malformed, the request should be rejected safely rather than passed into uncontrolled processing.



\---



\# 10. Ambiguity Handling



When multiple interpretations are possible, the system should prefer clarification over guessing.



Example:



User:

"Check my order."



If no order ID is available in the current session:



Assistant:

"Which order ID would you like me to check?"



The system should not select an arbitrary order.



\---



\# 11. Citation Behavior



Documentation and RAG-based responses should preserve source information.



When a response is based on retrieved documentation, the application should expose the available source information to the UI.



Conceptually:



Assistant response



&#x20;   â†“



Sources



\- FAQ

\- Return Policy

\- Other retrieved document/chunk metadata



The source information must originate from the retrieval pipeline.



The system must not fabricate citations.



\---



\# 12. Insufficient Evidence



If the documentation/RAG layer cannot provide sufficient evidence for an answer, the assistant should not fabricate an answer.



Expected behavior:



"I couldn't find enough information in the available documentation to answer that reliably."



The application should prefer an evidence-based fallback over hallucination.



\---



\# 13. Tool Failure Handling



If an approved tool fails, the application must not claim that the requested operation succeeded.



Expected behavior:



"I wasn't able to retrieve that information right now. Please try again."



The exact user-facing wording may be refined during implementation.



The important requirement is that tool failure is not converted into a fabricated successful result.



\---



\# 14. Unsupported Capability Handling



The application must clearly distinguish between:



\- a request that the system can perform

\- a request requiring clarification

\- a request for which evidence is insufficient

\- a request that is unsupported

\- a request where an approved tool failed



These cases must not be conflated.



\---



\# 15. Safety / Refusal Behavior



The application inherits the Week 9 controlled-agent safety model.



The system must not:



\- execute arbitrary Python

\- execute arbitrary SQL

\- modify customer records

\- delete records

\- cancel orders

\- issue refunds

\- perform unsupported side effects



The agent is read-only.



Requests for unavailable side effects should result in safe refusal.



\---



\# 16. Session Boundaries



Each conversational interaction should belong to a session.



A session provides the boundary for short-term conversational context.



Conceptually:



Session

â”‚

â”œâ”€â”€ Turn 1

â”œâ”€â”€ Turn 2

â”œâ”€â”€ Turn 3

â”œâ”€â”€ ...

â””â”€â”€ Current context



The session should have a unique identifier.



The application layer will use the session identifier to associate messages and context with the correct conversation.



\---



\# 17. Trace IDs



Each application request should be associated with a trace identifier.



Conceptually:



Request

&#x20;   â†“

Trace ID

&#x20;   â†“

Conversation layer

&#x20;   â†“

Agent

&#x20;   â†“

Tool/RAG

&#x20;   â†“

Response



The trace ID allows a request to be correlated across application and agent execution.



The Week 9 workflow already provides tracing information.



Week 10 will expose this information at the application boundary.



\---



\# 18. User Feedback



The application should support user feedback on assistant responses.



The initial feedback model should support:



\- positive feedback

\- negative feedback



Feedback should be associated with the relevant:



\- session

\- response

\- trace ID



This allows future evaluation and improvement.



\---



\# 19. Conversation State



The application distinguishes between different forms of state.



\## Session State



Short-term conversational context.



Examples:



\- recent user messages

\- recent assistant messages

\- current entity being discussed

\- current task context



\---



\## Durable Memory



Information intentionally stored using the Week 9 durable-memory subsystem.



Durable memory is separate from the knowledge base.



\---



\## Knowledge



Information retrieved from the Week 8 RAG system.



Knowledge should not be confused with user-specific memory.



\---



\# 20. Conversation Response Contract



The application should eventually expose a structured response contract.



Conceptually:



{

&#x20;   "session\_id": "...",

&#x20;   "trace\_id": "...",

&#x20;   "response": "...",

&#x20;   "sources": \[],

&#x20;   "tool\_used": null,

&#x20;   "status": "success"

}



The exact API schema will be defined during Day 2.



Possible status values include:



\- success

\- clarification

\- unsupported

\- insufficient\_evidence

\- tool\_error

\- validation\_error



The final schema will be implemented in the FastAPI layer.



\---



\# 21. Conversation Flow



The high-level conversation flow is:



User

&#x20;   â†“

Receive message

&#x20;   â†“

Identify intent

&#x20;   â†“

Check required information

&#x20;   â†“

Clarify if necessary

&#x20;   â†“

Send request to controlled agent

&#x20;   â†“

Select approved capability

&#x20;   â†“

Execute tool or RAG

&#x20;   â†“

Evaluate result

&#x20;   â†“

Synthesize response

&#x20;   â†“

Validate response

&#x20;   â†“

Attach source/trace information

&#x20;   â†“

Return response

&#x20;   â†“

Collect feedback



\---



\# 22. Happy Path Example â€” Documentation



User:

"How long do I have to return an item?"



Application:

Receives the message.



Agent:

Selects `documentation\_search`.



RAG:

Retrieves relevant documentation.



Agent:

Evaluates evidence.



Assistant:

Provides a grounded answer.



Application:

Returns the answer and available source information.



UI:

Displays response and sources.



\---



\# 23. Happy Path Example â€” Customer



User:

"Show me customer CUST-0001."



Agent:

Selects `customer\_lookup`.



Tool:

Validates the customer ID.



Tool:

Retrieves the matching customer.



Agent:

Evaluates the result.



Assistant:

Returns a concise customer summary.



\---



\# 24. Clarification Example



User:

"Check my order."



Assistant:

"Which order ID would you like me to check?"



User:

"ORD-000123."



Assistant:

Processes the order-status request using the supplied order ID.



\---



\# 25. Unsupported Request Example



User:

"Cancel ORD-000123."



System:



1\. Recognizes a destructive action.

2\. Does not call an unsupported tool.

3\. Does not pretend the cancellation happened.

4\. Returns a safe refusal.



Example:



"I can't cancel orders because order cancellation is not an available capability in this assistant."



\---



\# 26. Insufficient Evidence Example



User:

"What is the policy for a situation that is not covered by the documentation?"



RAG:

No sufficient evidence.



Assistant:



"I couldn't find enough information in the available documentation to answer that reliably."



\---



\# 27. Tool Failure Example



User:

"Show me customer CUST-0001."



Tool:

Fails unexpectedly.



Assistant:



"I wasn't able to retrieve that information right now. Please try again."



The application must not fabricate customer information.



\---



\# 28. Session Lifecycle



A conceptual session lifecycle is:



Create Session

&#x20;   â†“

Receive Message

&#x20;   â†“

Process Turn

&#x20;   â†“

Store Context

&#x20;   â†“

Return Response

&#x20;   â†“

Receive Next Message

&#x20;   â†“

Continue Session

&#x20;   â†“

Clear / End Session



The Week 10 UI will provide a clear-chat operation.



\---



\# 29. Clear Chat



The application must provide a mechanism to clear the active conversation.



Clear chat should remove the current conversational session context.



It should not automatically delete durable memory unless that behavior is explicitly designed and authorized.



Session state and durable memory remain separate.



\---



\# 30. Error States



The application should provide clear behavior for:



\- invalid input

\- missing identifiers

\- unsupported requests

\- tool failures

\- RAG failures

\- insufficient evidence

\- backend errors

\- network errors

\- unexpected application errors



Errors should be presented without exposing unnecessary internal implementation details.



\---



\# 31. Design Principles



The Week 10 conversational application follows these principles:



1\. Prefer the simplest correct mechanism.

2\. Use the existing Week 9 agent rather than rebuilding it.

3\. Use RAG when external project knowledge is required.

4\. Use approved tools for structured data access.

5\. Ask for clarification instead of guessing.

6\. Never fabricate tool results.

7\. Never fabricate citations.

8\. Refuse unsupported side effects.

9\. Keep session context separate from durable memory.

10\. Keep memory separate from knowledge retrieval.

11\. Preserve traceability.

12\. Provide user feedback mechanisms.

13\. Keep the application observable and testable.

14\. Preserve the safety boundaries established during Week 9.



\---



\# 32. Week 10 Acceptance Criteria â€” Day 1



Day 1 is complete when:



\- conversation intents are defined

\- turn-taking behavior is defined

\- clarification behavior is defined

\- multi-turn behavior is defined

\- citation behavior is defined

\- insufficient-evidence behavior is defined

\- refusal behavior is defined

\- fallback behavior is defined

\- session boundaries are defined

\- trace behavior is defined

\- feedback behavior is defined

\- application response concepts are defined

\- architecture is documented

\- component diagram is documented

\- sequence diagram is documented



The implementation will begin after the conversation design is finalized.
