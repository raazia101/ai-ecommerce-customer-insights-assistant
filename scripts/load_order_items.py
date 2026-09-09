import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Database connection
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")

url = (
    f"postgresql+psycopg://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(url)

# Load CSV
project_root = Path(__file__).resolve().parents[1]
file_path = project_root / "data" / "raw" / "order_items.csv"
df = pd.read_csv(file_path)

print(f"Loaded {len(df)} order-item records from CSV.")

# Validate required columns
required_columns = [
    "order_item_id",
    "order_id",
    "product_id",
    "quantity",
    "unit_price",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Validate order-item IDs
if df["order_item_id"].isna().any():
    raise ValueError("Found missing order_item IDs.")

if df["order_item_id"].duplicated().any():
    raise ValueError("Found duplicate order_item IDs.")

# Validate foreign-key fields
if df["order_id"].isna().any():
    raise ValueError("Found missing order IDs.")

if df["product_id"].isna().any():
    raise ValueError("Found missing product IDs.")

# Validate quantity
if (df["quantity"] <= 0).any():
    raise ValueError("Found order items with quantity <= 0.")

# Validate unit price
if (df["unit_price"] < 0).any():
    raise ValueError("Found order items with negative unit price.")

# Insert into PostgreSQL
insert_sql = text("""
    INSERT INTO order_items (
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price
    )
    VALUES (
        :order_item_id,
        :order_id,
        :product_id,
        :quantity,
        :unit_price
    )
""")

with engine.begin() as connection:
    for _, row in df.iterrows():
        connection.execute(
            insert_sql,
            {
                "order_item_id": row["order_item_id"],
                "order_id": row["order_id"],
                "product_id": row["product_id"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"],
            },
        )

print(f"Inserted {len(df)} order items into PostgreSQL.")