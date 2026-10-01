from pathlib import Path
from datetime import datetime, timezone

import os
import joblib
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ---------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "06_ml" / "artifacts" / "model_pipeline.joblib"
FEATURE_PATH = BASE_DIR / "data" / "curated" / "ml_customer_features.parquet"

MODEL_VERSION = "week5-logistic-regression-v1"

FEATURE_COLUMNS = [
    "country",
    "status",
    "customer_tenure_days",
    "completed_order_count",
    "completed_revenue",
    "average_order_value",
    "days_since_last_purchase",
    "has_previous_purchase",
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


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Main batch scoring
# ---------------------------------------------------------

def main():
    print("Starting batch scoring...")

    # Load model
    print(f"Loading model: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)

    # Load ML feature dataset
    print(f"Loading features: {FEATURE_PATH}")
    df = pd.read_parquet(FEATURE_PATH)

    if "customer_id" not in df.columns:
        raise ValueError("Feature dataset must contain customer_id.")

    missing_features = [
        column for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    # Prepare model input
    X = df[FEATURE_COLUMNS]

    # Generate predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    scored_at = datetime.now(timezone.utc)

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    try:
        with conn.cursor() as cur:

            sql = """
                INSERT INTO ml.predictions (
                    customer_id,
                    model_version,
                    prediction,
                    probability,
                    scored_at
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id, model_version)
                DO UPDATE SET
                    prediction = EXCLUDED.prediction,
                    probability = EXCLUDED.probability,
                    scored_at = EXCLUDED.scored_at;
            """

            rows = [
                (
                    str(customer_id),
                    MODEL_VERSION,
                    int(prediction),
                    float(probability),
                    scored_at,
                )
                for customer_id, prediction, probability
                in zip(
                    df["customer_id"],
                    predictions,
                    probabilities,
                )
            ]

            cur.executemany(sql, rows)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    print(f"Customers scored: {len(rows)}")
    print(f"Model version: {MODEL_VERSION}")
    print(f"Scored at: {scored_at.isoformat()}")
    print("Batch scoring completed successfully.")


if __name__ == "__main__":
    main()