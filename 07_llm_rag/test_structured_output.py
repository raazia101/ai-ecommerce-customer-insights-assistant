import pytest

from structured_output import parse_customer_insight


def test_valid_output():
    raw = """
    {
        "summary": "Customer is a repeat purchaser.",
        "customer_segment": "repeat",
        "confidence": 0.92
    }
    """

    result = parse_customer_insight(raw)

    assert result.customer_segment == "repeat"
    assert result.confidence == 0.92


def test_invalid_json():
    with pytest.raises(ValueError):
        parse_customer_insight("not json")


def test_missing_field():
    raw = """
    {
        "summary": "Customer is new.",
        "customer_segment": "new"
    }
    """

    with pytest.raises(ValueError):
        parse_customer_insight(raw)


def test_invalid_segment():
    raw = """
    {
        "summary": "Customer is active.",
        "customer_segment": "unknown",
        "confidence": 0.8
    }
    """

    with pytest.raises(ValueError):
        parse_customer_insight(raw)


def test_invalid_confidence():
    raw = """
    {
        "summary": "Customer is active.",
        "customer_segment": "repeat",
        "confidence": 1.5
    }
    """

    with pytest.raises(ValueError):
        parse_customer_insight(raw)