import pandas as pd
import pytest

from src.validation import (
    validate_required_columns,
    validate_no_missing_values,
    validate_unique_values,
    validate_positive_values,
    validate_non_negative_values,
)


def test_required_columns_pass():
    df = pd.DataFrame({
        "customer_id": ["CUST-001"],
        "email": ["test@example.com"],
    })

    validate_required_columns(
        df,
        ["customer_id", "email"],
    )


def test_required_columns_fail():
    df = pd.DataFrame({
        "customer_id": ["CUST-001"],
    })

    with pytest.raises(ValueError):
        validate_required_columns(
            df,
            ["customer_id", "email"],
        )


def test_no_missing_values_pass():
    df = pd.DataFrame({
        "customer_id": ["CUST-001", "CUST-002"],
    })

    validate_no_missing_values(
        df,
        ["customer_id"],
    )


def test_no_missing_values_fail():
    df = pd.DataFrame({
        "customer_id": ["CUST-001", None],
    })

    with pytest.raises(ValueError):
        validate_no_missing_values(
            df,
            ["customer_id"],
        )


def test_unique_values_pass():
    df = pd.DataFrame({
        "customer_id": ["CUST-001", "CUST-002"],
    })

    validate_unique_values(df, "customer_id")


def test_unique_values_fail():
    df = pd.DataFrame({
        "customer_id": ["CUST-001", "CUST-001"],
    })

    with pytest.raises(ValueError):
        validate_unique_values(df, "customer_id")


def test_positive_values_pass():
    df = pd.DataFrame({
        "quantity": [1, 2, 5],
    })

    validate_positive_values(df, "quantity")


def test_positive_values_fail():
    df = pd.DataFrame({
        "quantity": [1, 0, 5],
    })

    with pytest.raises(ValueError):
        validate_positive_values(df, "quantity")


def test_non_negative_values_pass():
    df = pd.DataFrame({
        "amount": [0, 10.50, 25.00],
    })

    validate_non_negative_values(df, "amount")


def test_non_negative_values_fail():
    df = pd.DataFrame({
        "amount": [10.00, -5.00],
    })

    with pytest.raises(ValueError):
        validate_non_negative_values(df, "amount")