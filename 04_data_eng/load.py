from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CURATED_DIR = BASE_DIR / "data" / "curated"


def load_parquet(
    dataframe: pd.DataFrame,
    filename: str,
) -> Path:
    """Write a DataFrame to the curated Parquet layer."""

    CURATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CURATED_DIR / filename

    dataframe.to_parquet(
        output_path,
        index=False,
    )

    print(
        f"Loaded {filename}: "
        f"{len(dataframe)} rows"
    )

    return output_path


def load_incremental_parquet(
    dataframe: pd.DataFrame,
    filename: str,
    key_column: str,
) -> Path:
    """
    Incrementally load data into an existing Parquet dataset.

    Existing records and new records are combined.
    Duplicate business keys are removed so reruns
    do not create duplicate records.
    """

    CURATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CURATED_DIR / filename

    if output_path.exists():
        existing_data = pd.read_parquet(
            output_path
        )

        combined_data = pd.concat(
            [
                existing_data,
                dataframe,
            ],
            ignore_index=True,
        )

        combined_data = combined_data.drop_duplicates(
            subset=[key_column],
            keep="last",
        )
    else:
        combined_data = dataframe.drop_duplicates(
            subset=[key_column]
        )

    combined_data.to_parquet(
        output_path,
        index=False,
    )

    print(
        f"Loaded {filename}: "
        f"{len(dataframe)} incoming rows, "
        f"{len(combined_data)} total rows"
    )

    return output_path


if __name__ == "__main__":
    test_data = pd.DataFrame({
        "customer_id": [
            "TEST-001",
            "TEST-002",
        ],
        "country": [
            "UAE",
            "India",
        ],
    })

    output_path = load_parquet(
        test_data,
        "test_customers.parquet",
    )

    print(
        f"Output path: {output_path}"
    )