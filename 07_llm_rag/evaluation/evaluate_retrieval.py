from pathlib import Path
import json
import sys


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GOLD_SET_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "evaluation"
    / "retrieval_gold_set.json"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "evaluation"
    / "retrieval_metrics.json"
)


# ============================================================
# Import retriever
# ============================================================

sys.path.insert(
    0,
    str(
        PROJECT_ROOT
        / "07_llm_rag"
    )
)

from retriever import retrieve


# ============================================================
# Load gold set
# ============================================================

gold_set = json.loads(
    GOLD_SET_PATH.read_text(
        encoding="utf-8"
    )
)


# ============================================================
# Evaluation configuration
# ============================================================

TOP_K = 5


# ============================================================
# Evaluation
# ============================================================

results = []

hit_count = 0

reciprocal_ranks = []

for item in gold_set:

    query = item["query"]

    expected_source = item[
        "expected_source"
    ]

    expected_section = item[
        "expected_section"
    ]

    retrieved = retrieve(
        query,
        top_k=TOP_K,
    )

    hit_rank = None

    for result in retrieved:

        metadata = result["metadata"]

        if (
            metadata["source"]
            == expected_source
            and metadata["section"]
            == expected_section
        ):

            hit_rank = result["rank"]
            break

    hit = hit_rank is not None

    if hit:

        hit_count += 1

        reciprocal_ranks.append(
            1 / hit_rank
        )

    else:

        reciprocal_ranks.append(
            0.0
        )

    results.append(
        {
            "query": query,
            "expected_source": expected_source,
            "expected_section": expected_section,
            "hit": hit,
            "hit_rank": hit_rank,
        }
    )


# ============================================================
# Calculate metrics
# ============================================================

total_queries = len(gold_set)

hit_rate_at_k = (
    hit_count / total_queries
    if total_queries
    else 0.0
)

mean_reciprocal_rank = (
    sum(reciprocal_ranks)
    / len(reciprocal_ranks)
    if reciprocal_ranks
    else 0.0
)


# ============================================================
# Save metrics
# ============================================================

metrics = {
    "evaluation_type": "semantic_retrieval",
    "top_k": TOP_K,
    "total_queries": total_queries,
    "hits": hit_count,
    "hit_rate_at_k": hit_rate_at_k,
    "mean_reciprocal_rank": mean_reciprocal_rank,
    "results": results,
}


METRICS_PATH.write_text(
    json.dumps(
        metrics,
        indent=2,
    ),
    encoding="utf-8",
)


# ============================================================
# Display results
# ============================================================

print("=" * 60)
print("RETRIEVAL EVALUATION")
print("=" * 60)

print(
    f"Queries evaluated: {total_queries}"
)

print(
    f"Hits@{TOP_K}: {hit_count}"
)

print(
    f"Hit Rate@{TOP_K}: "
    f"{hit_rate_at_k:.3f}"
)

print(
    f"Mean Reciprocal Rank: "
    f"{mean_reciprocal_rank:.3f}"
)

print()

for result in results:

    status = (
        "HIT"
        if result["hit"]
        else "MISS"
    )

    print(
        f"[{status}] "
        f"Rank={result['hit_rank']} "
        f"| {result['query']}"
    )

print()

print(
    f"Metrics saved to: {METRICS_PATH}"
)