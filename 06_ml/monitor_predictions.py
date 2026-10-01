from pathlib import Path

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_VERSION = "week5-logistic-regression-v1"

load_dotenv(BASE_DIR / ".env")


def main():
    database_url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    engine = create_engine(database_url)

    query = """
        SELECT
            prediction,
            probability,
            scored_at
        FROM ml.predictions
        WHERE model_version = %(model_version)s
        ORDER BY scored_at;
    """

    df = pd.read_sql_query(
        query,
        engine,
        params={"model_version": MODEL_VERSION},
    )

    engine.dispose()

    if df.empty:
        raise ValueError(
            f"No predictions found for model version: {MODEL_VERSION}"
        )

    print("Prediction monitoring")
    print("---------------------")
    print(f"Model version: {MODEL_VERSION}")
    print(f"Total predictions: {len(df)}")

    print("\nPrediction distribution:")
    print(
        df["prediction"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nPrediction proportions:")
    print(
        df["prediction"]
        .value_counts(normalize=True)
        .sort_index()
        .to_string()
    )

    print("\nProbability summary:")
    print(df["probability"].describe().to_string())

    print("\nScoring window:")
    print(f"First scored: {df['scored_at'].min()}")
    print(f"Last scored:  {df['scored_at'].max()}")


if __name__ == "__main__":
    main()