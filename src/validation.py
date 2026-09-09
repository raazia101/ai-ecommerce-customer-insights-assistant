import pandas as pd


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Check that all required columns are present."""
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_no_missing_values(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """Check that specified columns contain no missing values."""
    for column in columns:
        if df[column].isna().any():
            raise ValueError(
                f"Column '{column}' contains missing values."
            )


def validate_unique_values(
    df: pd.DataFrame,
    column: str,
) -> None:
    """Check that a column contains unique values."""
    if df[column].duplicated().any():
        raise ValueError(
            f"Column '{column}' contains duplicate values."
        )


def validate_positive_values(
    df: pd.DataFrame,
    column: str,
) -> None:
    """Check that all values are greater than zero."""
    if (df[column] <= 0).any():
        raise ValueError(
            f"Column '{column}' contains values <= 0."
        )


def validate_non_negative_values(
    df: pd.DataFrame,
    column: str,
) -> None:
    """Check that all values are zero or greater."""
    if (df[column] < 0).any():
        raise ValueError(
            f"Column '{column}' contains negative values."
        )