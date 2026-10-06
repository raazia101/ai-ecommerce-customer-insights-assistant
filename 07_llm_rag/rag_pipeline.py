from pathlib import Path
import json
import re

import chromadb
from sentence_transformers import SentenceTransformer
import tiktoken
from openai import OpenAI


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_STORE_DIR = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "artifacts"
    / "vector_store"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "artifacts"
    / "rag_results.json"
)

COLLECTION_NAME = "ecommerce_support"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_MODEL = "qwen2.5:3b"

TOP_K = 5

MAX_CONTEXT_TOKENS = 1200


# ============================================================
# Load embedding model
# ============================================================

print(f"Loading embedding model: {EMBEDDING_MODEL}")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ============================================================
# Connect to Chroma
# ============================================================

client = chromadb.PersistentClient(
    path=str(VECTOR_STORE_DIR)
)

collection = client.get_collection(
    COLLECTION_NAME
)

print(f"Collection: {COLLECTION_NAME}")
print(f"Stored chunks: {collection.count()}")


# ============================================================
# Connect to Ollama
# ============================================================

print(f"Connecting to local LLM: {LLM_MODEL}")

llm_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


# ============================================================
# Tokenizer
# ============================================================

tokenizer = tiktoken.get_encoding(
    "cl100k_base"
)


# ============================================================
# Text utilities
# ============================================================

def tokenize(text: str) -> set[str]:
    """
    Convert text into lowercase word tokens.
    """

    return set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )
    )


def keyword_overlap(
    query: str,
    document: str,
) -> float:
    """
    Calculate the proportion of query terms
    appearing in the document.
    """

    query_terms = tokenize(query)
    document_terms = tokenize(document)

    if not query_terms:
        return 0.0

    overlap = query_terms.intersection(
        document_terms
    )

    return len(overlap) / len(query_terms)


# ============================================================
# Semantic retrieval
# ============================================================

def retrieve(
    query: str,
    top_k: int = TOP_K,
):
    """
    Retrieve semantically relevant chunks
    from the Chroma vector store.
    """

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    retrieved = []

    if not results["documents"]:
        return retrieved

    for i in range(
        len(results["documents"][0])
    ):

        retrieved.append(
            {
                "rank": i + 1,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return retrieved


# ============================================================
# Hybrid retrieval
# ============================================================

def hybrid_retrieve(
    query: str,
    top_k: int = TOP_K,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
):
    """
    Combine semantic similarity and keyword overlap.

    semantic_score:
        1 / (1 + distance)

    final score:
        semantic_weight * semantic_score
        +
        keyword_weight * keyword_score
    """

    candidate_k = min(
        collection.count(),
        max(top_k * 2, 10),
    )

    semantic_results = retrieve(
        query=query,
        top_k=candidate_k,
    )

    ranked_results = []

    for result in semantic_results:

        keyword_score = keyword_overlap(
            query,
            result["text"],
        )

        semantic_score = 1 / (
            1 + result["distance"]
        )

        hybrid_score = (
            semantic_weight * semantic_score
            +
            keyword_weight * keyword_score
        )

        ranked_results.append(
            {
                **result,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "hybrid_score": hybrid_score,
            }
        )

    ranked_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    ranked_results = ranked_results[:top_k]

    for rank, result in enumerate(
        ranked_results,
        start=1,
    ):
        result["rank"] = rank

    return ranked_results


# ============================================================
# Build grounded context
# ============================================================

def build_context(
    results: list[dict],
    max_tokens: int = MAX_CONTEXT_TOKENS,
):
    """
    Build a token-budgeted context from retrieved chunks.

    Each source receives a citation ID such as [1], [2], etc.
    """

    context_parts = []

    used_tokens = 0

    sources = []

    for result in results:

        metadata = result["metadata"]

        source_id = len(sources) + 1

        source_text = (
            f"[{source_id}] "
            f"Source: {metadata['source']} | "
            f"Section: {metadata['section']} | "
            f"Page: {metadata.get('page', 'N/A')} | "
            f"Chunk: {metadata['chunk_index']}\n"
            f"{result['text']}"
        )

        source_tokens = len(
            tokenizer.encode(source_text)
        )

        if (
            used_tokens + source_tokens
            > max_tokens
        ):
            break

        context_parts.append(source_text)

        sources.append(
            {
                "citation": f"[{source_id}]",
                "source": metadata["source"],
                "section": metadata["section"],
                "page": metadata.get(
                    "page",
                    "N/A",
                ),
                "chunk_index": metadata[
                    "chunk_index"
                ],
                "distance": result["distance"],
            }
        )

        used_tokens += source_tokens

    context = "\n\n".join(
        context_parts
    )

    return (
        context,
        sources,
        used_tokens,
    )


# ============================================================
# Evidence check
# ============================================================

def has_sufficient_evidence(
    results: list[dict],
    threshold: float = 1.55,
):
    """
    Simple retrieval-based evidence gate.

    Lower Chroma distance indicates greater similarity.
    """

    if not results:
        return False

    best_distance = results[0]["distance"]

    return best_distance <= threshold


# ============================================================
# Grounded RAG prompt
# ============================================================

def build_prompt(
    question: str,
    context: str,
):
    """
    Build a strict grounded prompt.

    The prompt requires the model to:
    - use only retrieved evidence
    - answer the exact question
    - preserve concrete details
    - avoid vague summaries when specific evidence exists
    - cite every factual claim
    """

    return f"""
You are an e-commerce customer support assistant.

Answer the user's question using ONLY the provided
retrieved evidence.

STRICT RULES:

1. Do not invent information.

2. Do not use outside knowledge.

3. Answer the user's exact question directly.

4. Every factual claim in your answer MUST have a citation.

5. If evidence exists, include at least one citation such
   as [1], [2], or [3].

6. Preserve important factual details from the evidence.

7. IMPORTANT: If the evidence contains a specific number,
   timeframe, date, percentage, limit, condition, requirement,
   name, option, or list that directly answers the question,
   you MUST include that specific information.

8. Do NOT replace a specific answer with a vague summary.

   For example:
   - If the evidence gives a refund timeframe, state the
     actual timeframe rather than only saying that it
     depends on the payment provider.
   - If the evidence lists payment methods, list those
     payment methods rather than only saying that supported
     methods are shown at checkout.
   - If the evidence gives a return period, state the
     exact return period.
   - If the evidence gives conditions or requirements,
     include the relevant conditions or requirements.

9. Match the type of answer requested by the question.

   - "How long" -> give the timeframe.
   - "How many" -> give the number.
   - "What" -> provide the specific item, option, or list.
   - "Which" -> identify the relevant options.
   - "Why" -> provide the supported reasons.
   - "Can I" -> clearly state whether it is allowed and
     include relevant conditions.
   - "How do I" -> provide the supported steps.

10. Do not omit an important numerical value,
    timeframe, list item, condition, or requirement
    when it directly answers the question.

11. Do not add details that are not present in the
    retrieved evidence.

12. Never output the raw source block instead of an answer.

13. Do not mention information that is absent from the
    retrieved evidence.

14. If the evidence does not contain enough information,
    say exactly:

    "I don't have enough information in the available
    support documents to answer that question."

15. When multiple sources support the answer, cite the
    relevant sources.

16. Put citations directly after the factual statement
    they support.

17. Keep the answer concise, but do not sacrifice
    important evidence needed to answer the question.

18. Before finalizing the answer, check:
    - Did I answer exactly what was asked?
    - Did I preserve any important number or timeframe?
    - Did I preserve any important list or set of options?
    - Did I preserve relevant conditions or requirements?
    - Does every factual claim have a citation?
    - Did I avoid information outside the evidence?

Retrieved evidence:

{context}

User question:

{question}

Now provide the concise, specific, evidence-grounded answer.
""".strip()


# ============================================================
# Generate answer
# ============================================================

def generate_answer(
    question: str,
    context: str,
):
    """
    Generate an answer using Qwen2.5 3B
    through Ollama's OpenAI-compatible API.
    """

    prompt = build_prompt(
        question,
        context,
    )

    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a grounded customer "
                    "support assistant. "
                    "Follow the evidence and citation "
                    "rules exactly. "
                    "Answer the exact question and "
                    "preserve concrete details from "
                    "the retrieved evidence."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()


# ============================================================
# Run RAG pipeline
# ============================================================

def run_rag(
    question: str,
):
    """
    Execute the complete RAG pipeline:

        Query
          ↓
        Hybrid retrieval
          ↓
        Evidence gate
          ↓
        Context construction
          ↓
        Local LLM generation
          ↓
        Source citations
    """

    print()
    print("=" * 70)
    print("RAG PIPELINE")
    print("=" * 70)

    print(
        f"Question: {question}"
    )

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    results = hybrid_retrieve(
        query=question,
        top_k=TOP_K,
    )

    print()
    print("Retrieved chunks:")

    for result in results:

        print(
            f"  Rank {result['rank']} | "
            f"Hybrid score: "
            f"{result['hybrid_score']:.4f} | "
            f"Distance: "
            f"{result['distance']:.4f} | "
            f"{result['metadata']['source']} | "
            f"{result['metadata']['section']}"
        )

    # --------------------------------------------------------
    # Evidence gate
    # --------------------------------------------------------

    evidence_sufficient = (
        has_sufficient_evidence(results)
    )

    # --------------------------------------------------------
    # Build context and generate
    # --------------------------------------------------------

    context = ""
    sources = []
    context_tokens = 0

    if evidence_sufficient:

        (
            context,
            sources,
            context_tokens,
        ) = build_context(
            results,
            MAX_CONTEXT_TOKENS,
        )

        print()
        print(
            f"Context tokens: "
            f"{context_tokens}"
        )

        answer = generate_answer(
            question,
            context,
        )

    else:

        answer = (
            "I don't have enough information "
            "in the available support documents "
            "to answer that question."
        )

    # --------------------------------------------------------
    # Result object
    # --------------------------------------------------------

    result = {
        "question": question,
        "model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "top_k": TOP_K,
        "evidence_sufficient": evidence_sufficient,
        "context_tokens": context_tokens,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": [
            {
                "rank": item["rank"],
                "source": item["metadata"]["source"],
                "section": item["metadata"]["section"],
                "page": item["metadata"].get(
                    "page",
                    "N/A",
                ),
                "chunk_index": item[
                    "metadata"
                ]["chunk_index"],
                "distance": item["distance"],
                "semantic_score": item[
                    "semantic_score"
                ],
                "keyword_score": item[
                    "keyword_score"
                ],
                "hybrid_score": item[
                    "hybrid_score"
                ],
            }
            for item in results
        ],
    }

    return result


# ============================================================
# Save result
# ============================================================

def save_result(
    result: dict,
):
    """
    Save the RAG result as JSON.
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"RAG result saved to: "
        f"{OUTPUT_PATH}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    test_question = (
        "How long do I have to return an item?"
    )

    result = run_rag(
        test_question
    )

    print()
    print("=" * 70)
    print("GENERATED ANSWER")
    print("=" * 70)

    print(
        result["answer"]
    )

    print()
    print("=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print(
            f"{source['citation']} "
            f"{source['source']} | "
            f"{source['section']} | "
            f"Page: {source['page']}"
        )

    save_result(result)