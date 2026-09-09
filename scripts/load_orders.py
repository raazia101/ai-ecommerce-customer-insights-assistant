import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os
from pathlib import Path

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
file_path = project_root / "data" / "raw" / "orders.csv"
df = pd.read_csv(file_path)

print(f"Loaded {len(df)} order records from CSV.")

# Validate required columns
required_columns = [
    "order_id",
    "customer_id",
    "order_date",
    "status",
    "currency",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Validate order IDs
if df["order_id"].isna().any():
    raise ValueError("Found missing order IDs.")

if df["order_id"].duplicated().any():
    raise ValueError("Found duplicate order IDs.")

# Validate customer IDs
if df["customer_id"].isna().any():
    raise ValueError("Found missing customer IDs.")

# Convert order date
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="raise"
)

# Insert into PostgreSQL
insert_sql = text("""
    INSERT INTO orders (
        order_id,
        customer_id,
        order_date,
        status,
        currency
    )
    VALUES (
        :order_id,
        :customer_id,
        :order_date,
        :status,
        :currency
    )
""")

with engine.begin() as connection:
    for _, row in df.iterrows():
        connection.execute(
            insert_sql,
            {
                "order_id": row["order_id"],
                "customer_id": row["customer_id"],
                "order_date": row["order_date"],
                "status": row["status"],
                "currency": row["currency"],
            },
        )

print(f"Inserted {len(df)} orders into PostgreSQL.")