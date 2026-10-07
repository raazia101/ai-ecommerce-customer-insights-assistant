# Week 9 — Agent Architecture

## 1. Purpose

The purpose of this week is to transform the existing e-commerce
customer-support RAG pipeline into a bounded AI agent capable of:

- understanding the user's request,
- deciding which tool is appropriate,
- calling typed tools,
- retrieving information from the RAG knowledge base,
- maintaining state during a task,
- validating intermediate results,
- terminating safely,
- and producing a grounded final response.

The agent does not replace the Week 8 RAG system.

Instead, RAG becomes one of the tools available to the agent.

---

# 2. Chatbot vs RAG Pipeline vs Workflow vs Agent

## 2.1 Chatbot

A chatbot primarily performs conversational interaction.

Typical flow:

User
→ Language Model
→ Response

A basic chatbot does not necessarily retrieve external information,
call tools, maintain structured state, or make decisions about
which external capability should be used.

---

## 2.2 RAG Pipeline

The Week 8 system is a Retrieval-Augmented Generation pipeline.

Its flow is:

User Question
→ Query Embedding
→ Semantic Retrieval
→ Keyword Retrieval
→ Hybrid Ranking
→ Evidence Gate
→ Context Construction
→ Grounded Prompt
→ Local LLM
→ Answer + Citations

The RAG system is specialized for answering questions using the
available support documentation.

It is not itself a general-purpose agent.

---

## 2.3 Workflow

A workflow is a predefined sequence of operations.

Example:

Understand Request
→ Retrieve Information
→ Synthesize
→ Validate
→ Respond

The sequence is explicitly controlled by the application.

Workflows are useful when the required process is predictable.

---

## 2.4 Agent

An agent introduces controlled decision-making.

Instead of always following one fixed sequence, the controller can
determine which available tool or operation is appropriate for the
current request.

Example:

User:
"What is the status of order ORD-1001?"

Agent reasoning:

1. Identify the request as an order-status request.
2. Select the order-status tool.
3. Validate the order ID.
4. Execute the tool.
5. Inspect the result.
6. Synthesize the response.
7. Validate the response.
8. Terminate.

Another request:

"What is your return policy?"

Agent reasoning:

1. Identify this as a documentation question.
2. Select the documentation/RAG tool.
3. Retrieve relevant evidence.
4. Generate a grounded response.
5. Return citations.
6. Terminate.

---

# 3. Agent Architecture

The Week 9 agent follows this architecture:

User
  |
  v
Agent Controller
  |
  +-----------------------+
  |                       |
  v                       v
Understand Request      State
  |
  v
Tool Selection
  |
  +-------------------+------------------+-------------------+
  |                   |                  |                   |
  v                   v                  v                   v
Customer Lookup    Order Status      KPI Query        Documentation Search
                                                         |
                                                         v
                                                    Week 8 RAG
  |
  v
Tool Result
  |
  v
Synthesis
  |
  v
Validation
  |
  +-------> Retry if recoverable
  |
  v
Final Response
  |
  v
Termination

---

# 4. Agent Components

The agent consists of the following components.

## 4.1 Language Model

The language model is responsible for interpreting natural-language
requests and generating the final response.

The existing project uses:

- Model: Qwen2.5:3b
- Runtime: Ollama
- API interface: OpenAI-compatible endpoint
- Endpoint: http://localhost:11434/v1

The Week 9 agent can therefore reuse the same local model infrastructure
already established during Week 8.

---

## 4.2 Instructions

The agent must operate under explicit instructions.

Important instructions include:

- use only available tools,
- do not invent tool results,
- validate tool arguments,
- do not access unauthorized information,
- do not perform unsupported actions,
- keep tool usage bounded,
- stop when the task is complete,
- return a clear response,
- preserve evidence and citations when using RAG.

---

## 4.3 Tools

The initial tool set contains four typed read-oriented tools:

1. Customer Lookup
2. Order Status
3. KPI Query
4. Documentation Search

Documentation Search connects the agent to the Week 8 RAG pipeline.

---

## 4.4 State

The agent maintains state during execution.

State may include:

- session ID,
- user request,
- current step,
- selected tool,
- tool arguments,
- tool results,
- retrieved sources,
- intermediate response,
- validation status,
- final response,
- trace information.

---

## 4.5 Control Loop

The agent operates through a bounded control loop:

1. Understand request
2. Select action
3. Validate action
4. Execute tool
5. Inspect result
6. Synthesize
7. Validate
8. Respond or continue

The loop must have explicit limits.

---

## 4.6 Termination

The agent must terminate when:

- the user's request has been answered,
- required evidence has been obtained,
- a safe answer cannot be produced,
- a tool fails beyond the retry limit,
- the maximum number of steps is reached,
- or the request requires an unsupported action.

There must never be an unlimited tool-calling loop.

---

# 5. Tool Safety

The Week 9 implementation primarily uses read-only tools.

Read-only tools may execute automatically when their arguments are valid.

Potential future side-effecting operations such as:

- cancelling orders,
- issuing refunds,
- modifying customer records,
- changing account information,

must require explicit user approval before execution.

The agent must never infer approval for a side effect.

---

# 6. Bounded Agent Design

The agent uses explicit safety boundaries.

Example limits:

MAX_STEPS = 6
MAX_TOOL_RETRIES = 2
MAX_TOOL_RESULT_LENGTH = 2000 characters

These limits prevent:

- infinite loops,
- excessive tool usage,
- uncontrolled latency,
- excessive token consumption,
- accidental repeated calls.

---

# 7. Error Handling

Tool errors must be converted into controlled results.

Examples:

Invalid customer ID
→ validation error

Invalid order ID
→ validation error

Unsupported KPI
→ tool error

RAG unavailable
→ controlled fallback

Tool timeout
→ retry once or twice

Repeated failure
→ terminate safely

The language model must never fabricate a successful result when a
tool failed.

---

# 8. Week 8 RAG Integration

The existing Week 8 RAG pipeline remains responsible for
documentation-based questions.

The agent treats it as a specialized documentation search capability.

Example:

User:
"How long do I have to return an item?"

Agent:
→ Documentation Search
→ Week 8 hybrid retrieval
→ Evidence gate
→ Qwen2.5 grounded generation
→ Citation-backed answer

This preserves the existing RAG architecture while allowing the
agent to decide when RAG should be used.

---

# 9. Agent Decision Guide

| User Request | Tool |
|---|---|
| Customer information | customer_lookup |
| Order status | order_status |
| Business metric / KPI | kpi_query |
| Policy / FAQ / documentation | documentation_search |
| Unsupported request | no tool / safe fallback |

Examples:

"What is the status of ORD-1001?"
→ order_status

"Show me customer CUST-0001."
→ customer_lookup

"What is the average order value?"
→ kpi_query

"How long do I have to return an item?"
→ documentation_search

"Can you cancel my order?"
→ unsupported side-effect unless approval workflow exists

---

# 10. Agent vs Week 8 RAG

Week 8:

User
→ RAG
→ Answer

Week 9:

User
→ Agent
→ Decide what capability is required
→ Tool
→ Result
→ Validate
→ Answer

Therefore Week 9 extends the existing system rather than replacing it.

---

# 11. Target Architecture

The final Week 9 architecture is:

                 USER
                   |
                   v
             AGENT CONTROLLER
                   |
            UNDERSTAND REQUEST
                   |
                   v
             TOOL SELECTION
                   |
       +-----------+-----------+-----------+
       |           |           |           |
       v           v           v           v
   CUSTOMER      ORDER       KPI       DOCUMENTATION
    LOOKUP      STATUS      QUERY         SEARCH
                                           |
                                           v
                                      WEEK 8 RAG
                                           |
       +-----------+-----------+-----------+
                   |
                   v
              TOOL RESULT
                   |
                   v
               SYNTHESIZE
                   |
                   v
               VALIDATE
                   |
             +-----+-----+
             |           |
          Retry       Complete
             |           |
             +           v
                      RESPONSE

---

# 12. Design Principle

The agent is not designed to maximize autonomy.

It is designed to maximize:

- correctness,
- bounded behavior,
- traceability,
- grounded responses,
- predictable tool usage,
- safe termination.

The system should therefore be considered a bounded
customer-support agent rather than an unrestricted autonomous agent.