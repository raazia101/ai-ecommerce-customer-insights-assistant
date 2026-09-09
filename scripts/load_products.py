import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")

database_url = (
    f"postgresql+psycopg://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(database_url)

project_root = Path(__file__).resolve().parents[1]
csv_path = project_root / "data" / "raw" / "products.csv"

df = pd.read_csv(csv_path)

print(f"Loaded {len(df)} product records from CSV.")

required_columns = {
    "product_id",
    "product_name",
    "category",
    "price",
    "stock_quantity",
    "status",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

if df["product_id"].isna().any():
    raise ValueError("product_id contains missing values.")

if df["product_id"].duplicated().any():
    raise ValueError("product_id contains duplicates.")

if (df["price"] < 0).any():
    raise ValueError("price contains negative values.")

if (df["stock_quantity"] < 0).any():
    raise ValueError("stock_quantity contains negative values.")

with engine.begin() as connection:
    connection.execute(
        text(
            """
            INSERT INTO products (
                product_id,
                product_name,
                category,
                price,
                stock_quantity,
                status
            )
            VALUES (
                :product_id,
                :product_name,
                :category,
                :price,
                :stock_quantity,
                :status
            )
            """
        ),
        df.to_dict(orient="records"),
    )

print(f"Inserted {len(df)} products into PostgreSQL.")