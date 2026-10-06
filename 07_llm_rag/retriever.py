from pathlib import Path
import re

import chromadb
from sentence_transformers import SentenceTransformer


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

COLLECTION_NAME = "ecommerce_support"

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 5


# ============================================================
# Load embedding model
# ============================================================

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)


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
# Text utilities
# ============================================================

def tokenize(text: str) -> set[str]:
    """
    Convert text into a set of lowercase word tokens.
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
    that appear in the document.
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
    max_distance: float | None = None,
    source: str | None = None,
    section: str | None = None,
):
    """
    Retrieve the most semantically relevant chunks.

    Optional filters:
    - max_distance
    - source
    - section
    """

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]

    # --------------------------------------------------------
    # Build metadata filters
    # --------------------------------------------------------

    filters = []

    if source is not None:
        filters.append(
            {"source": source}
        )

    if section is not None:
        filters.append(
            {"section": section}
        )

    where = None

    if len(filters) == 1:
        where = filters[0]

    elif len(filters) > 1:
        where = {
            "$and": filters
        }

    # --------------------------------------------------------
    # Query Chroma
    # --------------------------------------------------------

    query_kwargs = {
        "query_embeddings": [
            query_embedding.tolist()
        ],
        "n_results": top_k,
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    if where is not None:
        query_kwargs["where"] = where

    results = collection.query(
        **query_kwargs
    )

    # --------------------------------------------------------
    # Process results
    # --------------------------------------------------------

    retrieved = []

    if not results["documents"]:
        return retrieved

    for i in range(
        len(results["documents"][0])
    ):

        distance = results["distances"][0][i]

        if (
            max_distance is not None
            and distance > max_distance
        ):
            continue

        retrieved.append(
            {
                "rank": len(retrieved) + 1,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance,
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
    source: str | None = None,
    section: str | None = None,
):
    """
    Combine semantic retrieval with keyword overlap.

    The semantic score is derived from Chroma distance:

        semantic_score = 1 / (1 + distance)

    The final score is:

        final_score =
            semantic_weight * semantic_score
            +
            keyword_weight * keyword_score

    This is a simple baseline for comparison rather than
    a production-grade ranking algorithm.
    """

    if not 0 <= semantic_weight <= 1:
        raise ValueError(
            "semantic_weight must be between 0 and 1."
        )

    if not 0 <= keyword_weight <= 1:
        raise ValueError(
            "keyword_weight must be between 0 and 1."
        )

    if abs(
        semantic_weight + keyword_weight - 1.0
    ) > 1e-9:

        raise ValueError(
            "semantic_weight + keyword_weight "
            "must equal 1."
        )

    # Retrieve a larger candidate set before
    # applying hybrid ranking.
    candidate_k = min(
        collection.count(),
        max(top_k * 2, 10),
    )

    semantic_results = retrieve(
        query=query,
        top_k=candidate_k,
        source=source,
        section=section,
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

        final_score = (
            semantic_weight * semantic_score
            +
            keyword_weight * keyword_score
        )

        ranked_results.append(
            {
                **result,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "hybrid_score": final_score,
            }
        )

    ranked_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    for rank, result in enumerate(
        ranked_results[:top_k],
        start=1,
    ):
        result["rank"] = rank

    return ranked_results[:top_k]


# ============================================================
# Display semantic retrieval results
# ============================================================

def print_results(
    query: str,
    results: list[dict],
    title: str = "RETRIEVAL TEST",
):
    """Print standard retrieval results."""

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    print(f"Query: {query}")

    if not results:
        print("\nNo relevant results found.")
        return

    for result in results:

        print()
        print(f"Rank: {result['rank']}")
        print(
            f"Distance: "
            f"{result['distance']:.4f}"
        )
        print(
            f"Source: "
            f"{result['metadata']['source']}"
        )
        print(
            f"Section: "
            f"{result['metadata']['section']}"
        )
        print(
            f"Chunk index: "
            f"{result['metadata']['chunk_index']}"
        )
        print(
            f"Text: "
            f"{result['text']}"
        )


# ============================================================
# Display hybrid retrieval results
# ============================================================

def print_hybrid_results(
    query: str,
    results: list[dict],
):
    """Print hybrid retrieval results."""

    print()
    print("=" * 60)
    print("HYBRID RETRIEVAL TEST")
    print("=" * 60)

    print(f"Query: {query}")

    if not results:
        print("\nNo relevant results found.")
        return

    for result in results:

        print()
        print(f"Rank: {result['rank']}")

        print(
            f"Hybrid score: "
            f"{result['hybrid_score']:.4f}"
        )

        print(
            f"Semantic score: "
            f"{result['semantic_score']:.4f}"
        )

        print(
            f"Keyword score: "
            f"{result['keyword_score']:.4f}"
        )

        print(
            f"Distance: "
            f"{result['distance']:.4f}"
        )

        print(
            f"Source: "
            f"{result['metadata']['source']}"
        )

        print(
            f"Section: "
            f"{result['metadata']['section']}"
        )

        print(
            f"Text: "
            f"{result['text']}"
        )


# ============================================================
# Manual tests
# ============================================================

if __name__ == "__main__":

    test_query = "Why was my payment declined?"

    # --------------------------------------------------------
    # Test 1: Basic semantic retrieval
    # --------------------------------------------------------

    semantic_results = retrieve(
        test_query,
        top_k=5,
    )

    print_results(
        test_query,
        semantic_results,
        title="SEMANTIC RETRIEVAL TEST",
    )

    # --------------------------------------------------------
    # Test 2: Source filtering
    # --------------------------------------------------------

    source_results = retrieve(
        test_query,
        top_k=5,
        source="policies.md",
    )

    print_results(
        test_query,
        source_results,
        title="SOURCE-FILTERED RETRIEVAL",
    )

    # --------------------------------------------------------
    # Test 3: Section filtering
    # --------------------------------------------------------

    section_results = retrieve(
        test_query,
        top_k=5,
        section="Payment Policy",
    )

    print_results(
        test_query,
        section_results,
        title="SECTION-FILTERED RETRIEVAL",
    )

    # --------------------------------------------------------
    # Test 4: Hybrid retrieval
    # --------------------------------------------------------

    hybrid_results = hybrid_retrieve(
        test_query,
        top_k=5,
        semantic_weight=0.7,
        keyword_weight=0.3,
    )

    print_hybrid_results(
        test_query,
        hybrid_results,
    )