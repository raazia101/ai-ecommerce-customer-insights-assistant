# Week 7 — Prompt Patterns Catalog

## 1. System Instructions

Define the role, behavior, boundaries, and objectives of the assistant.

Example:

You are an e-commerce customer insights assistant.
Provide concise, factual business insights.
Do not invent information that is not present in the supplied data.

---

## 2. Task Context

Provide the information required to perform the task.

Example:

Customer:
- Customer ID: CUST-0001
- Completed orders: 8
- Average order value: 145 AED
- Last purchase: 14 days ago

Task:
Summarize the customer's purchasing behavior.

---

## 3. Constraints

Explicitly define what the model should and should not do.

Example:

- Use only the supplied customer information.
- Do not invent missing values.
- Keep the response under 100 words.
- Clearly distinguish facts from assumptions.

---

## 4. Examples

Provide examples of desired input/output behavior.

Example:

Input:
Customer purchased 5 times and spent AED 800.

Output:
The customer is an active repeat purchaser with AED 800 in recorded
spending.

---

## 5. Output Contract

Specify the required output structure.

Example:

Return JSON with:

{
  "summary": "...",
  "customer_segment": "...",
  "confidence": 0.0
}

---

## 6. Zero-Shot Prompting

The model receives instructions without examples.

Example:

Classify the customer as:
- new
- repeat
- high_value

Customer has completed 8 orders.

---

## 7. Few-Shot Prompting

The model receives examples before the new task.

Example:

Customer with 1 order → new

Customer with 8 orders → repeat

Customer with 20 orders and high spending → high_value

Now classify:

Customer has completed 8 orders.

---

## Prompt Construction Pattern

A reliable prompt can be structured as:

1. System instructions
2. Task
3. Context/data
4. Constraints
5. Examples
6. Output contract

# Prompt Pattern Comparison

| Pattern | Purpose | Strength | Risk |
|---|---|---|---|
| System instruction | Define behavior | Consistent role | Overly broad instructions |
| Task context | Supply information | Better relevance | Context growth |
| Constraints | Control behavior | Reduces unwanted output | Too many constraints |
| Examples | Demonstrate behavior | Clarifies expected output | Example bias |
| Output contract | Control format | Easier parsing | Invalid outputs can still occur |
| Zero-shot | No examples | Simple and efficient | May be less consistent |
| Few-shot | Uses examples | Demonstrates desired behavior | Uses additional context |
