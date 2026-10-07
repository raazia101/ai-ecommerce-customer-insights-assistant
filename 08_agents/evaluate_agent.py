"""
Week 9 - Agent Evaluation

Evaluates the deterministic agent workflow against a small
representative evaluation set.

Metrics:
    - Tool selection accuracy
    - Task completion rate
    - Average workflow steps
    - Average tool attempts
    - Average latency
    - Per-category performance

The evaluation is intentionally deterministic so that the
results can be repeated and compared across revisions.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

AGENTS_DIR = PROJECT_ROOT / "08_agents"

EVALUATION_FILE = (
    AGENTS_DIR / "agent_evaluation.csv"
)

WORKFLOW_FILE = (
    AGENTS_DIR / "agent_workflow.py"
)


# ============================================================
# Dynamic module loading
# ============================================================

def load_module_from_path(
    module_name: str,
    file_path: Path,
):
    """
    Dynamically import a Python module from a file path.

    This is required because the project contains folders such
    as 08_agents that cannot be imported using normal dotted
    Python import syntax.
    """

    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module from {file_path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# Load the Week 9 agent workflow.
agent_workflow = load_module_from_path(
    "week9_agent_workflow_evaluation",
    WORKFLOW_FILE,
)


# ============================================================
# Evaluation data
# ============================================================

def load_evaluation_cases() -> list[dict[str, Any]]:
    """
    Load evaluation cases from agent_evaluation.csv.
    """

    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: "
            f"{EVALUATION_FILE}"
        )

    cases: list[dict[str, Any]] = []

    with EVALUATION_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            expected_tool = (
                row["expected_tool"].strip()
            )

            # The CSV uses "none" to represent the absence
            # of a selected tool.
            if expected_tool.lower() == "none":
                expected_tool = None

            expected_success = (
                row["expected_success"]
                .strip()
                .lower()
                == "true"
            )

            cases.append(
                {
                    "case_id": row["case_id"].strip(),
                    "category": row["category"].strip(),
                    "question": row["question"].strip(),
                    "expected_tool": expected_tool,
                    "expected_success": expected_success,
                }
            )

    return cases


# ============================================================
# Display helpers
# ============================================================

def display_tool_name(
    tool: str | None,
) -> str:
    """
    Convert a tool value into a safe display string.

    None is displayed as 'none' so that formatted output
    does not raise a TypeError.
    """

    if tool is None:
        return "none"

    return str(tool)


# ============================================================
# Single-case evaluation
# ============================================================

def evaluate_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute one evaluation case and determine whether it passes.
    """

    start_time = time.perf_counter()

    result = agent_workflow.run_agent(
        case["question"]
    )

    end_time = time.perf_counter()

    latency_ms = (
        end_time - start_time
    ) * 1000

    actual_tool = result.get(
        "selected_tool"
    )

    expected_tool = case[
        "expected_tool"
    ]

    actual_success = bool(
        result.get("success", False)
    )

    expected_success = bool(
        case["expected_success"]
    )

    # --------------------------------------------------------
    # Tool-selection correctness
    # --------------------------------------------------------

    tool_match = (
        actual_tool == expected_tool
    )

    # --------------------------------------------------------
    # Task-success correctness
    # --------------------------------------------------------

    success_match = (
        actual_success == expected_success
    )

    # --------------------------------------------------------
    # Overall case result
    # --------------------------------------------------------

    passed = (
        tool_match
        and success_match
    )

    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "question": case["question"],
        "expected_tool": expected_tool,
        "actual_tool": actual_tool,
        "expected_success": expected_success,
        "actual_success": actual_success,
        "tool_match": tool_match,
        "success_match": success_match,
        "passed": passed,
        "step_count": result.get(
            "step_count",
            0,
        ),
        "tool_attempts": result.get(
            "tool_attempts",
            0,
        ),
        "latency_ms": latency_ms,
        "answer": result.get(
            "answer",
            "",
        ),
        "errors": result.get(
            "errors",
            [],
        ),
        "terminated": result.get(
            "terminated",
            False,
        ),
        "trace": result.get(
            "trace",
            [],
        ),
    }


# ============================================================
# Evaluate all cases
# ============================================================

def evaluate_all_cases(
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Run every evaluation case.
    """

    results: list[dict[str, Any]] = []

    for case in cases:

        result = evaluate_case(case)

        results.append(result)

    return results


# ============================================================
# Aggregate metrics
# ============================================================

def calculate_metrics(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate overall evaluation metrics.
    """

    total_cases = len(results)

    if total_cases == 0:
        return {
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "tool_selection_accuracy": 0.0,
            "task_completion_rate": 0.0,
            "average_steps": 0.0,
            "average_tool_attempts": 0.0,
            "average_latency_ms": 0.0,
        }

    passed_cases = sum(
        1
        for result in results
        if result["passed"]
    )

    failed_cases = (
        total_cases - passed_cases
    )

    tool_matches = sum(
        1
        for result in results
        if result["tool_match"]
    )

    success_matches = sum(
        1
        for result in results
        if result["success_match"]
    )

    average_steps = (
        sum(
            result["step_count"]
            for result in results
        )
        / total_cases
    )

    average_tool_attempts = (
        sum(
            result["tool_attempts"]
            for result in results
        )
        / total_cases
    )

    average_latency_ms = (
        sum(
            result["latency_ms"]
            for result in results
        )
        / total_cases
    )

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "tool_selection_accuracy": (
            tool_matches / total_cases
        ),
        "task_completion_rate": (
            success_matches / total_cases
        ),
        "average_steps": average_steps,
        "average_tool_attempts": (
            average_tool_attempts
        ),
        "average_latency_ms": (
            average_latency_ms
        ),
    }


# ============================================================
# Category metrics
# ============================================================

def calculate_category_metrics(
    results: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Calculate metrics separately for each evaluation category.
    """

    categories: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for result in results:

        category = result["category"]

        categories.setdefault(
            category,
            [],
        ).append(result)

    category_metrics: dict[
        str,
        dict[str, Any],
    ] = {}

    for category, category_results in categories.items():

        count = len(category_results)

        passed = sum(
            1
            for result in category_results
            if result["passed"]
        )

        tool_matches = sum(
            1
            for result in category_results
            if result["tool_match"]
        )

        success_matches = sum(
            1
            for result in category_results
            if result["success_match"]
        )

        average_steps = (
            sum(
                result["step_count"]
                for result in category_results
            )
            / count
        )

        average_latency = (
            sum(
                result["latency_ms"]
                for result in category_results
            )
            / count
        )

        category_metrics[category] = {
            "cases": count,
            "passed": passed,
            "pass_rate": passed / count,
            "tool_selection_accuracy": (
                tool_matches / count
            ),
            "task_completion_rate": (
                success_matches / count
            ),
            "average_steps": average_steps,
            "average_latency_ms": average_latency,
        }

    return category_metrics


# ============================================================
# Report printing
# ============================================================

def print_report(
    results: list[dict[str, Any]],
) -> None:
    """
    Print a human-readable evaluation report.
    """

    metrics = calculate_metrics(
        results
    )

    category_metrics = (
        calculate_category_metrics(
            results
        )
    )

    print()
    print("=" * 70)
    print("AGENT EVALUATION REPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # Case results
    # --------------------------------------------------------

    print()
    print("CASE RESULTS")
    print("-" * 80)

    for result in results:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        expected_display = display_tool_name(
            result["expected_tool"]
        )

        actual_display = display_tool_name(
            result["actual_tool"]
        )

        print(
            f"{result['case_id']} | "
            f"{status} | "
            f"{actual_display:22} | "
            f"expected={expected_display:22} | "
            f"actual={actual_display:22} | "
            f"steps={result['step_count']} | "
            f"latency={result['latency_ms']:.2f}ms"
        )

    # --------------------------------------------------------
    # Overall metrics
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("OVERALL METRICS")
    print("=" * 70)

    print(
        f"Total cases: "
        f"{metrics['total_cases']}"
    )

    print(
        f"Passed cases: "
        f"{metrics['passed_cases']}"
    )

    print(
        f"Failed cases: "
        f"{metrics['failed_cases']}"
    )

    print(
        "Tool selection accuracy: "
        f"{metrics['tool_selection_accuracy']:.3f}"
    )

    print(
        "Task completion rate: "
        f"{metrics['task_completion_rate']:.3f}"
    )

    print(
        "Average workflow steps: "
        f"{metrics['average_steps']:.2f}"
    )

    print(
        "Average tool attempts: "
        f"{metrics['average_tool_attempts']:.2f}"
    )

    print(
        "Average latency: "
        f"{metrics['average_latency_ms']:.2f} ms"
    )

    # --------------------------------------------------------
    # Category metrics
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("CATEGORY METRICS")
    print("=" * 70)

    for category, values in category_metrics.items():

        print()
        print(
            f"Category: {category}"
        )

        print(
            f"  Cases: "
            f"{values['cases']}"
        )

        print(
            f"  Passed: "
            f"{values['passed']}"
        )

        print(
            f"  Pass rate: "
            f"{values['pass_rate']:.3f}"
        )

        print(
            "  Tool selection accuracy: "
            f"{values['tool_selection_accuracy']:.3f}"
        )

        print(
            "  Task completion rate: "
            f"{values['task_completion_rate']:.3f}"
        )

        print(
            "  Average steps: "
            f"{values['average_steps']:.2f}"
        )

        print(
            "  Average latency: "
            f"{values['average_latency_ms']:.2f} ms"
        )

    # --------------------------------------------------------
    # Failed cases
    # --------------------------------------------------------

    failed_results = [
        result
        for result in results
        if not result["passed"]
    ]

    if failed_results:

        print()
        print("=" * 70)
        print("FAILED CASE DETAILS")
        print("=" * 70)

        for result in failed_results:

            print()
            print(
                f"{result['case_id']} "
                f"({result['category']})"
            )

            print(
                f"Question: "
                f"{result['question']}"
            )

            print(
                f"Expected tool: "
                f"{display_tool_name(result['expected_tool'])}"
            )

            print(
                f"Actual tool: "
                f"{display_tool_name(result['actual_tool'])}"
            )

            print(
                f"Expected success: "
                f"{result['expected_success']}"
            )

            print(
                f"Actual success: "
                f"{result['actual_success']}"
            )

            if result["errors"]:

                print("Errors:")

                for error in result["errors"]:

                    print(
                        f"  - {error}"
                    )

    print()
    print("=" * 70)


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Run the complete Week 9 agent evaluation.
    """

    print(
        "Loading Week 9 agent evaluation..."
    )

    cases = load_evaluation_cases()

    print(
        f"Loaded {len(cases)} evaluation cases."
    )

    results = evaluate_all_cases(
        cases
    )

    print_report(results)


if __name__ == "__main__":
    main()