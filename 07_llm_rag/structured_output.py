from dataclasses import dataclass
from typing import Any
import json


@dataclass
class CustomerInsight:
    summary: str
    customer_segment: str
    confidence: float


ALLOWED_SEGMENTS = {
    "new",
    "repeat",
    "high_value",
}


def parse_customer_insight(raw_output: str) -> CustomerInsight:
    """
    Parse and validate an LLM-generated JSON response.
    """

    try:
        data: Any = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError("Output is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("Output must be a JSON object.")

    required_fields = {
        "summary",
        "customer_segment",
        "confidence",
    }

    missing = required_fields - data.keys()

    if missing:
        raise ValueError(
            f"Missing required fields: {sorted(missing)}"
        )

    if not isinstance(data["summary"], str):
        raise ValueError("summary must be a string.")

    if data["customer_segment"] not in ALLOWED_SEGMENTS:
        raise ValueError("Invalid customer_segment.")

    confidence = data["confidence"]

    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be numeric.")

    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1.")

    return CustomerInsight(
        summary=data["summary"],
        customer_segment=data["customer_segment"],
        confidence=float(confidence),
    )