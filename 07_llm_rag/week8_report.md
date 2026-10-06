# Week 8 — Retrieval-Augmented Generation (RAG)

## Project
E-commerce Customer Insights Assistant

## Week Objective

The objective of Week 8 was to build a source-grounded Retrieval-Augmented Generation (RAG) system capable of answering e-commerce customer-support questions using retrieved FAQ and policy documents.

The week focused on separating and evaluating two major components:

1. Retrieval — finding the most relevant evidence from the knowledge base.
2. Generation — producing an answer grounded only in the retrieved evidence.

The system was designed to avoid unsupported answers and to explicitly indicate when the available documents do not contain sufficient evidence.

---

# 1. Week 8 Architecture

The completed RAG pipeline follows this flow:

User Question
       ↓
Question Embedding
       ↓
Semantic Retrieval
       ↓
Keyword Retrieval
       ↓
Hybrid Retrieval
       ↓
Top-K Relevant Chunks
       ↓
Evidence Sufficiency Check
       ↓
Context Construction
       ↓
Local LLM (Qwen2.5 3B via Ollama)
       ↓
Grounded Answer + Citations
       ↓
Evaluation

The system therefore separates retrieval from answer generation rather than allowing the language model to answer independently from the knowledge base.

---

# 2. Day 1 — Embeddings and Semantic Similarity

## Objective

Understand how text embeddings can represent semantic meaning and how similarity between embeddings can be used to identify related customer-support questions.

## Model

The embedding model used was:

all-MiniLM-L6-v2

Embedding dimension:

384

## Dataset

A small set of 13 customer-support sentences was created covering topics such as:

- Orders
- Returns
- Payments
- Accounts
- Store support

Each sentence was converted into a 384-dimensional embedding.

## Similarity

Cosine similarity was used to compare the embeddings.

Higher cosine similarity indicates that two pieces of text are semantically closer.

A similarity matrix was generated and stored at:

07_llm_rag/artifacts/similarity_matrix.csv

## Dimensionality Reduction

PCA was used to reduce the 384-dimensional embeddings to two dimensions for visualization.

This allowed semantic relationships between the customer-support examples to be visually inspected.

## Deliverable

07_llm_rag/embeddings_intro.ipynb

---

# 3. Day 2 — Document Processing and Vector Store

## Objective

Create a small searchable knowledge base from FAQ and policy documents.

## Source Documents

Two Markdown documents were created:

07_llm_rag/data/faq.md

07_llm_rag/data/policies.md

The FAQ contains customer-support questions and answers.

The policy document contains formal policies covering areas such as:

- Returns
- Refunds
- Shipping
- Payments
- Account security
- Cancellation

## Chunking

The Markdown files were split into sections using Markdown headings.

The chunks were cleaned and assigned metadata.

Chunk configuration:

- Chunk size: 120
- Overlap: 20

## Metadata

Each chunk stores metadata including:

- Source filename
- Section
- Page
- Chunk index

This metadata is later used to display the source of retrieved information.

## Vector Store

Chroma was used as the persistent vector database.

Collection:

ecommerce_support

Embedding model:

all-MiniLM-L6-v2

Embedding dimension:

384

Total documents:

2

Total chunks:

14

Vector store location:

07_llm_rag/artifacts/vector_store

## Index Metadata

Versioning information is stored in:

07_llm_rag/artifacts/index_metadata.json

Deterministic SHA-256 identifiers were used for stored chunks so that indexing remains reproducible.

## Deliverable

07_llm_rag/build_vector_store.py

---

# 4. Day 3 — Retrieval System

## Objective

Build and evaluate a retrieval system capable of finding relevant evidence for customer-support questions.

## Semantic Retrieval

The user's query is converted into an embedding using:

all-MiniLM-L6-v2

Chroma then searches the vector store for semantically similar chunks.

## Keyword Retrieval

Keyword overlap was also calculated between the query and retrieved document text.

This provides an additional lexical signal.

## Hybrid Retrieval

Semantic and keyword signals were combined.

The current hybrid weighting is:

Semantic similarity: 70%

Keyword overlap: 30%

This allows the system to benefit from both semantic meaning and exact keyword matches.

## Metadata Filtering

The retriever supports filtering by:

- Source
- Section

It also supports:

- top-k retrieval
- distance thresholds
- score inspection

## Retrieval Gold Set

An 8-question retrieval evaluation set was created.

The questions cover:

1. Return period
2. Payment declines
3. Order tracking
4. Delivery status
5. Password reset
6. Refund timing
7. Order cancellation
8. Payment methods

Each question has an expected source and section.

## Retrieval Results

The retrieval evaluation produced:

Queries evaluated: 8

Hit Rate@5: 1.000

MRR: 0.812

All 8 evaluation questions successfully retrieved the expected source within the top 5 results.

The expected source appeared at rank 1 for the first five questions and at rank 2 for the remaining three.

## Deliverables

07_llm_rag/retriever.py

07_llm_rag/evaluation/retrieval_gold_set.json

07_llm_rag/evaluation/evaluate_retrieval.py

07_llm_rag/artifacts/retrieval_metrics.json

---

# 5. Day 4 — Grounded RAG Pipeline

## Objective

Combine retrieval with a local language model to generate answers grounded in retrieved evidence.

## Local LLM

The project originally supported hosted OpenAI generation, but the OpenAI API could not be used because the available API quota was exhausted.

Therefore, the Week 8 generation pipeline was implemented locally using:

Ollama

Model:

qwen2.5:3b

The model was accessed through Ollama's OpenAI-compatible local endpoint.

This allowed the complete RAG system to operate locally without depending on external LLM API credits.

## Context Construction

The top retrieved chunks are converted into a structured evidence context.

Each source is assigned a citation number:

[1]
[2]
[3]

and so on.

The context is kept within a token budget.

Current context token budget:

1200 tokens

## Evidence Sufficiency Gate

Before calling the language model, the system checks whether the retrieved evidence is sufficiently relevant.

If the best retrieval distance is above the configured threshold, the system does not generate an answer.

Instead, it returns:

"I don't have enough information in the available support documents to answer that question."

This prevents the model from answering questions when the knowledge base does not provide adequate evidence.

## Grounded Generation

The generation prompt instructs the model to:

- Use only retrieved evidence
- Avoid outside knowledge
- Avoid inventing information
- Answer directly
- Preserve important factual details
- Include citations
- Cite factual claims
- Avoid unsupported information
- Refuse when evidence is insufficient

## Example

Question:

How long do I have to return an item?

Generated answer:

Eligible products can generally be returned within 30 days of delivery. [1]

## Insufficient Evidence Test

Question:

Do you offer student discounts?

The system correctly determined that the available documents did not contain sufficient evidence and returned the refusal response without making an unsupported LLM-generated claim.

## Deliverable

07_llm_rag/rag_pipeline.py

---

# 6. Day 5 — RAG Evaluation

## Objective

Evaluate retrieval and generation separately.

The evaluation measures:

- Source accuracy
- Citation rate
- Answer relevance
- Faithfulness
- Evidence failure rate
- Expected source rank
- Mean source rank
- Source MRR

## Evaluation Set

The generation evaluation uses 8 customer-support questions.

The same core topics used during retrieval evaluation were used to test the complete RAG pipeline.

## Final Results

| Metric | Result |
|---|---:|
| Queries | 8 |
| Source Accuracy | 1.000 |
| Citation Rate | 1.000 |
| Answer Relevance | 0.750 |
| Faithfulness | 1.000 |
| Evidence Failure Rate | 0.000 |
| Mean Source Rank | 1.250 |
| Source MRR | 0.875 |

## Interpretation

### Source Accuracy — 100%

All eight evaluation questions successfully retrieved the expected source within the evaluated results.

This indicates that the retrieval component is consistently finding the appropriate document.

### Citation Rate — 100%

Every generated answer contained a source citation.

This provides traceability from generated answers back to retrieved evidence.

### Faithfulness — 100%

All evaluated answers were judged faithful to the retrieved evidence.

The generator therefore did not introduce unsupported external information in the evaluated examples.

### Evidence Failure Rate — 0%

No question that passed through the generation stage was incorrectly treated as unsupported.

The separate evidence sufficiency mechanism also correctly rejected an example question about student discounts where the knowledge base did not provide sufficient information.

### Answer Relevance — 75%

Six out of eight evaluation cases were marked relevant by the evaluation system.

The lower relevance score primarily reflects cases where the local 3B model produced a somewhat general answer instead of preserving the most specific detail requested by the question.

For example, the refund question received relevant refund-policy evidence, but the generated answer emphasized that timing depends on the payment provider or bank instead of providing a more specific timeframe.

This demonstrates an important distinction between retrieval quality and generation quality.

---

# 7. Retrieval vs Generation Findings

One of the main objectives of Week 8 was to evaluate retrieval separately from generation.

The results demonstrate that the retrieval system performs strongly:

- Retrieval Hit Rate@5: 100%
- Retrieval MRR: 0.812
- Generation source accuracy: 100%
- Generation faithfulness: 100%

However, the answer relevance score was 75%.

This shows that strong retrieval does not automatically guarantee that the language model will produce the most complete or precise answer.

The system can retrieve the correct evidence while the local language model may summarize that evidence too generally.

This is an important limitation of using a smaller local language model.

---

# 8. Prompt Injection / Grounding Considerations

The RAG prompt explicitly instructs the model to:

- Follow retrieved evidence
- Ignore outside knowledge
- Avoid unsupported claims
- Preserve factual details
- Cite evidence
- Refuse when evidence is insufficient

The architecture also limits the model's context to retrieved customer-support documents.

This reduces the risk of the model generating unsupported customer-support information.

---

# 9. Technologies Used

## Python

Main implementation language.

## Sentence Transformers

Used for semantic embeddings.

Model:

all-MiniLM-L6-v2

## Chroma

Used as the persistent vector database.

## scikit-learn

Used for:

- PCA
- evaluation-related utilities

## Ollama

Used to run the local language model.

## Qwen2.5 3B

Used as the local generation model.

## tiktoken

Used for approximate context token counting.

## NumPy / Pandas

Used for numerical processing and evaluation artifacts.

---

# 10. Main Week 8 Files

```text
07_llm_rag/
│
├── data/
│   ├── faq.md
│   └── policies.md
│
├── evaluation/
│   ├── retrieval_gold_set.json
│   ├── evaluate_retrieval.py
│   ├── rag_eval_set.json
│   └── evaluate_rag.py
│
├── artifacts/
│   ├── similarity_matrix.csv
│   ├── retrieval_metrics.json
│   ├── rag_generation_metrics.json
│   ├── index_metadata.json
│   └── vector_store/
│
├── embeddings_intro.ipynb
├── build_vector_store.py
├── retriever.py
├── rag_pipeline.py
└── week8_report.md