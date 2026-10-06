"""
Week 8 - Day 5
RAG Generation Evaluation

Measures:
1. Source accuracy
2. Expected source rank
3. Citation rate
4. Answer relevance
5. Faithfulness / groundedness
6. Evidence failure handling
7. Source MRR

Uses the existing run_rag() interface.
"""

import importlib.util
import json
import re
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAG_PIPELINE_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "rag_pipeline.py"
)

EVAL_SET_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "evaluation"
    / "rag_eval_set.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "07_llm_rag"
    / "artifacts"
    / "rag_generation_metrics.json"
)


# ============================================================
# LOAD RAG PIPELINE
# ============================================================

def load_rag_pipeline():

    spec = importlib.util.spec_from_file_location(
        "rag_pipeline",
        RAG_PIPELINE_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Could not load RAG pipeline from {RAG_PIPELINE_PATH}"
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# ============================================================
# LOAD EVALUATION SET
# ============================================================

def load_eval_set():

    with open(
        EVAL_SET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# EXPECTED FIELD HELPERS
# ============================================================

def get_expected_source(item):
    """
    Support the existing evaluation-set naming convention
    as well as the simpler source name.
    """

    return (
        item.get("expected_source")
        or item.get("source")
        or item.get("expected_document")
        or item.get("document")
    )


def get_expected_section(item):
    """
    Support multiple section naming conventions.
    """

    return (
        item.get("expected_section")
        or item.get("section")
        or item.get("expected_chunk")
        or item.get("chunk")
    )


def get_expected_answer_points(item):
    """
    Support multiple possible answer-point field names.
    """

    points = (
        item.get("expected_answer_points")
        or item.get("answer_points")
        or item.get("expected_points")
        or item.get("answer")
        or []
    )

    if isinstance(points, str):
        return [points]

    return points


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# SOURCE ACCURACY
# ============================================================

def evaluate_source_accuracy(result, item):

    expected_source = get_expected_source(item)
    expected_section = get_expected_section(item)

    retrieved_sources = result.get(
        "sources",
        [],
    )

    for source in retrieved_sources:

        source_match = (
            source.get("source")
            == expected_source
        )

        section_match = (
            expected_section is None
            or source.get("section")
            == expected_section
        )

        if source_match and section_match:
            return True

    return False


# ============================================================
# SOURCE RANK
# ============================================================

def get_expected_source_rank(result, item):

    expected_source = get_expected_source(item)
    expected_section = get_expected_section(item)

    retrieved_chunks = result.get(
        "retrieved_chunks",
        [],
    )

    for chunk in retrieved_chunks:

        source_match = (
            chunk.get("source")
            == expected_source
        )

        section_match = (
            expected_section is None
            or chunk.get("section")
            == expected_section
        )

        if source_match and section_match:

            return chunk.get("rank")

    return None


# ============================================================
# CITATION RATE
# ============================================================

def evaluate_citations(answer):

    if not answer:
        return False

    return bool(
        re.search(
            r"\[\d+\]",
            str(answer),
        )
    )


# ============================================================
# ANSWER RELEVANCE
# ============================================================

def evaluate_answer_relevance(answer, item):

    if not answer:
        return False

    normalized_answer = normalize_text(
        answer
    )

    expected_points = (
        get_expected_answer_points(item)
    )

    if not expected_points:
        return True

    matched = 0

    for point in expected_points:

        normalized_point = normalize_text(
            point
        )

        if not normalized_point:
            continue

        # Exact phrase match
        if normalized_point in normalized_answer:
            matched += 1
            continue

        # Token overlap
        point_tokens = set(
            normalized_point.split()
        )

        answer_tokens = set(
            normalized_answer.split()
        )

        if not point_tokens:
            continue

        overlap = (
            len(
                point_tokens
                & answer_tokens
            )
            / len(point_tokens)
        )

        if overlap >= 0.50:
            matched += 1

    return matched == len(
        expected_points
    )


# ============================================================
# FAITHFULNESS
# ============================================================

def evaluate_faithfulness(result):

    evidence_sufficient = result.get(
        "evidence_sufficient",
        False,
    )

    sources = result.get(
        "sources",
        [],
    )

    answer = result.get(
        "answer",
        "",
    )

    return (
        evidence_sufficient
        and bool(sources)
        and evaluate_citations(answer)
    )


# ============================================================
# EVIDENCE FAILURE
# ============================================================

def evaluate_evidence_failure(result):

    evidence_sufficient = result.get(
        "evidence_sufficient",
        True,
    )

    answer = str(
        result.get(
            "answer",
            "",
        )
    ).lower()

    refusal_patterns = [
        "i don't have enough information",
        "i do not have enough information",
        "not enough information",
        "insufficient evidence",
        "available support documents",
    ]

    refusal = any(
        pattern in answer
        for pattern in refusal_patterns
    )

    return (
        not evidence_sufficient
        and refusal
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("WEEK 8 - RAG GENERATION EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load pipeline
    # --------------------------------------------------------

    print("\nLoading RAG pipeline...")

    rag_pipeline = load_rag_pipeline()

    if not hasattr(
        rag_pipeline,
        "run_rag",
    ):

        raise AttributeError(
            "rag_pipeline.py does not expose run_rag()."
        )

    print("run_rag() found.")

    # --------------------------------------------------------
    # Load evaluation set
    # --------------------------------------------------------

    eval_set = load_eval_set()

    print(
        f"Evaluation queries: {len(eval_set)}"
    )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    total = len(eval_set)

    source_correct_count = 0
    citation_count = 0
    relevance_count = 0
    faithfulness_count = 0
    evidence_failure_count = 0

    results = []

    # ========================================================
    # RUN EVALUATIONS
    # ========================================================

    for index, item in enumerate(
        eval_set,
        start=1,
    ):

        question = item["question"]

        expected_source = (
            get_expected_source(item)
        )

        expected_section = (
            get_expected_section(item)
        )

        print("\n" + "-" * 70)

        print(
            f"Question {index}/{total}"
        )

        print(question)

        print("-" * 70)

        print(
            f"Expected source: "
            f"{expected_source}"
        )

        print(
            f"Expected section: "
            f"{expected_section}"
        )

        # ----------------------------------------------------
        # Run RAG
        # ----------------------------------------------------

        result = rag_pipeline.run_rag(
            question
        )

        if not isinstance(
            result,
            dict,
        ):

            raise TypeError(
                "run_rag() must return a dictionary."
            )

        answer = str(
            result.get(
                "answer",
                "",
            )
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        source_correct = (
            evaluate_source_accuracy(
                result,
                item,
            )
        )

        expected_rank = (
            get_expected_source_rank(
                result,
                item,
            )
        )

        citation_present = (
            evaluate_citations(
                answer
            )
        )

        answer_relevant = (
            evaluate_answer_relevance(
                answer,
                item,
            )
        )

        faithful = (
            evaluate_faithfulness(
                result
            )
        )

        evidence_failure = (
            evaluate_evidence_failure(
                result
            )
        )

        # ----------------------------------------------------
        # Counts
        # ----------------------------------------------------

        if source_correct:
            source_correct_count += 1

        if citation_present:
            citation_count += 1

        if answer_relevant:
            relevance_count += 1

        if faithful:
            faithfulness_count += 1

        if evidence_failure:
            evidence_failure_count += 1

        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        print("\nAnswer:")
        print(answer)

        print("\nMetrics:")

        print(
            f"  Source correct:     "
            f"{source_correct}"
        )

        print(
            f"  Expected source rank:"
            f" {expected_rank}"
        )

        print(
            f"  Citation present:   "
            f"{citation_present}"
        )

        print(
            f"  Answer relevant:    "
            f"{answer_relevant}"
        )

        print(
            f"  Faithfulness:       "
            f"{faithful}"
        )

        print(
            f"  Evidence failure:   "
            f"{evidence_failure}"
        )

        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        sources = result.get(
            "sources",
            [],
        )

        if sources:

            print(
                "\nRetrieved sources:"
            )

            for source in sources:

                distance = source.get(
                    "distance"
                )

                if isinstance(
                    distance,
                    (int, float),
                ):

                    distance_text = (
                        f"{distance:.4f}"
                    )

                else:

                    distance_text = "N/A"

                print(
                    f"  "
                    f"{source.get('citation')} "
                    f"{source.get('source')} | "
                    f"{source.get('section')} | "
                    f"distance={distance_text}"
                )

        # ----------------------------------------------------
        # Save per-question result
        # ----------------------------------------------------

        results.append(
            {
                "question_id": item.get(
                    "id",
                    f"q{index}",
                ),

                "question": question,

                "expected_source": (
                    expected_source
                ),

                "expected_section": (
                    expected_section
                ),

                "expected_answer_points": (
                    get_expected_answer_points(
                        item
                    )
                ),

                "answer": answer,

                "evidence_sufficient": (
                    result.get(
                        "evidence_sufficient"
                    )
                ),

                "context_tokens": (
                    result.get(
                        "context_tokens"
                    )
                ),

                "source_correct": (
                    source_correct
                ),

                "expected_source_rank": (
                    expected_rank
                ),

                "citation_present": (
                    citation_present
                ),

                "answer_relevant": (
                    answer_relevant
                ),

                "faithful": (
                    faithful
                ),

                "evidence_failure": (
                    evidence_failure
                ),

                "sources": sources,
            }
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    source_accuracy = (
        source_correct_count / total
        if total
        else 0
    )

    citation_rate = (
        citation_count / total
        if total
        else 0
    )

    answer_relevance_rate = (
        relevance_count / total
        if total
        else 0
    )

    faithfulness_rate = (
        faithfulness_count / total
        if total
        else 0
    )

    evidence_failure_rate = (
        evidence_failure_count / total
        if total
        else 0
    )

    # --------------------------------------------------------
    # Rank metrics
    # --------------------------------------------------------

    ranks = [
        result["expected_source_rank"]
        for result in results
        if result["expected_source_rank"]
        is not None
    ]

    if ranks:

        mean_source_rank = (
            sum(ranks) / len(ranks)
        )

        reciprocal_ranks = [
            1 / rank
            for rank in ranks
        ]

        source_mrr = (
            sum(reciprocal_ranks)
            / len(reciprocal_ranks)
        )

    else:

        mean_source_rank = None
        source_mrr = 0

    # ========================================================
    # SUMMARY OBJECT
    # ========================================================

    summary = {

        "queries": total,

        "source_accuracy": round(
            source_accuracy,
            3,
        ),

        "citation_rate": round(
            citation_rate,
            3,
        ),

        "answer_relevance_rate": round(
            answer_relevance_rate,
            3,
        ),

        "faithfulness_rate": round(
            faithfulness_rate,
            3,
        ),

        "evidence_failure_rate": round(
            evidence_failure_rate,
            3,
        ),

        "mean_source_rank": (
            round(
                mean_source_rank,
                3,
            )
            if mean_source_rank is not None
            else None
        ),

        "source_mrr": round(
            source_mrr,
            3,
        ),
    }

    # ========================================================
    # SAVE JSON
    # ========================================================

    output = {

        "evaluation": "rag_generation",

        "model": getattr(
            rag_pipeline,
            "LLM_MODEL",
            "unknown",
        ),

        "embedding_model": getattr(
            rag_pipeline,
            "EMBEDDING_MODEL",
            "unknown",
        ),

        "top_k": getattr(
            rag_pipeline,
            "TOP_K",
            None,
        ),

        "summary": summary,

        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Queries:                 {total}"
    )

    print(
        f"Source accuracy:         "
        f"{source_accuracy:.3f}"
    )

    print(
        f"Citation rate:           "
        f"{citation_rate:.3f}"
    )

    print(
        f"Answer relevance rate:   "
        f"{answer_relevance_rate:.3f}"
    )

    print(
        f"Faithfulness rate:       "
        f"{faithfulness_rate:.3f}"
    )

    print(
        f"Evidence failure rate:   "
        f"{evidence_failure_rate:.3f}"
    )

    if mean_source_rank is not None:

        print(
            f"Mean source rank:        "
            f"{mean_source_rank:.3f}"
        )

    else:

        print(
            "Mean source rank:        N/A"
        )

    print(
        f"Source MRR:              "
        f"{source_mrr:.3f}"
    )

    print("\nSaved:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print(
        "RAG GENERATION EVALUATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()