from pathlib import Path
import os

import numpy as np
import pandas as pd
import psycopg2


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "curated"
    / "ml_customer_features.parquet"
)


NUMERICAL_COLUMNS = [
    "customer_tenure_days",
    "completed_order_count",
    "completed_revenue",
    "average_order_value",
    "days_since_last_purchase",
    "total_transaction_count",
    "failed_transaction_count",
    "refunded_transaction_count",
    "unique_products_purchased",
    "unique_categories_purchased",
    "total_event_count",
    "product_view_count",
    "add_to_cart_count",
    "checkout_started_count",
    "search_count",
    "login_count",
    "purchase_count",
    "remove_from_cart_count",
]


def get_connection():
    password = os.getenv("PGPASSWORD")

    if not password:
        raise RuntimeError(
            "PGPASSWORD environment variable is not set."
        )

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "intern_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=password,
    )


def load_predictions():
    conn = get_connection()

    try:
        query = """
            SELECT
                customer_id,
                model_version,
                prediction,
                probability,
                scored_at
            FROM ml.predictions
            ORDER BY scored_at;
        """

        return pd.read_sql_query(query, conn)

    finally:
        conn.close()


def prediction_distribution():
    predictions = load_predictions()

    counts = (
        predictions["prediction"]
        .value_counts()
        .sort_index()
    )

    probabilities = predictions["probability"]

    print("=== Prediction Distribution ===")
    print(f"Total predictions: {len(predictions)}")
    print(f"Predicted 0: {counts.get(0, 0)}")
    print(f"Predicted 1: {counts.get(1, 0)}")
    print(f"Mean probability: {probabilities.mean():.4f}")
    print(f"Min probability: {probabilities.min():.4f}")
    print(f"Max probability: {probabilities.max():.4f}")

    print("\nModel versions:")
    print(predictions["model_version"].value_counts())


def feature_summary():
    df = pd.read_parquet(DATA_PATH)

    print("\n=== Reference Feature Statistics ===")

    for column in NUMERICAL_COLUMNS:
        values = df[column].dropna()

        print(
            f"{column}: "
            f"mean={values.mean():.4f}, "
            f"std={values.std():.4f}, "
            f"min={values.min():.4f}, "
            f"max={values.max():.4f}"
        )


def missing_values():
    df = pd.read_parquet(DATA_PATH)

    print("\n=== Missing Value Monitoring ===")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values detected.")
    else:
        print(missing)


def calculate_psi(reference, current, bins=10):
    reference = pd.Series(reference).dropna()
    current = pd.Series(current).dropna()

    breakpoints = np.percentile(
        reference,
        np.linspace(0, 100, bins + 1)
    )

    breakpoints = np.unique(breakpoints)

    if len(breakpoints) < 3:
        return 0.0

    reference_bins = pd.cut(
        reference,
        bins=breakpoints,
        include_lowest=True
    )

    current_bins = pd.cut(
        current,
        bins=breakpoints,
        include_lowest=True
    )

    reference_distribution = (
        reference_bins
        .value_counts(normalize=True)
        .sort_index()
    )

    current_distribution = (
        current_bins
        .value_counts(normalize=True)
        .sort_index()
    )

    reference_distribution, current_distribution = (
        reference_distribution.align(
            current_distribution,
            fill_value=0
        )
    )

    epsilon = 0.0001

    reference_distribution = (
        reference_distribution + epsilon
    )

    current_distribution = (
        current_distribution + epsilon
    )

    psi = (
        (current_distribution - reference_distribution)
        * np.log(
            current_distribution
            / reference_distribution
        )
    ).sum()

    return float(psi)


def drift_report():
    df = pd.read_parquet(DATA_PATH)

    print("\n=== Feature Drift Report ===")

    for column in NUMERICAL_COLUMNS:
        values = df[column].dropna()

        # Current smoke test:
        # reference and current use the same dataset.
        psi = calculate_psi(values, values)

        if psi < 0.10:
            status = "LOW"
        elif psi < 0.25:
            status = "MODERATE"
        else:
            status = "HIGH"

        print(
            f"{column}: "
            f"PSI={psi:.4f} "
            f"({status})"
        )


def main():
    print("ML Monitoring Report")
    print("====================")

    prediction_distribution()
    feature_summary()
    missing_values()
    drift_report()

    print("\nMonitoring completed.")


if __name__ == "__main__":
    main()
