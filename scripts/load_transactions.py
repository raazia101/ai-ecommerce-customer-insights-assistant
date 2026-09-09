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
file_path = project_root / "data" / "raw" / "transactions.csv"
df = pd.read_csv(file_path)

print(f"Loaded {len(df)} transaction records from CSV.")

# Validate required columns
required_columns = [
    "transaction_id",
    "order_id",
    "customer_id",
    "amount",
    "currency",
    "payment_method",
    "status",
    "transaction_date",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Validate transaction IDs
if df["transaction_id"].isna().any():
    raise ValueError("Found missing transaction IDs.")

if df["transaction_id"].duplicated().any():
    raise ValueError("Found duplicate transaction IDs.")

# Validate foreign-key fields
if df["order_id"].isna().any():
    raise ValueError("Found missing order IDs.")

if df["customer_id"].isna().any():
    raise ValueError("Found missing customer IDs.")

# Validate transaction amounts
if (df["amount"] < 0).any():
    raise ValueError("Found transactions with negative amounts.")

# Convert transaction date
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="raise"
)

# Insert into PostgreSQL
insert_sql = text("""
    INSERT INTO transactions (
        transaction_id,
        order_id,
        customer_id,
        amount,
        currency,
        payment_method,
        status,
        transaction_date
    )
    VALUES (
        :transaction_id,
        :order_id,
        :customer_id,
        :amount,
        :currency,
        :payment_method,
        :status,
        :transaction_date
    )
""")

with engine.begin() as connection:
    for _, row in df.iterrows():
        connection.execute(
            insert_sql,
            {
                "transaction_id": row["transaction_id"],
                "order_id": row["order_id"],
                "customer_id": row["customer_id"],
                "amount": row["amount"],
                "currency": row["currency"],
                "payment_method": row["payment_method"],
                "status": row["status"],
                "transaction_date": row["transaction_date"],
            },
        )

print(f"Inserted {len(df)} transactions into PostgreSQL.")