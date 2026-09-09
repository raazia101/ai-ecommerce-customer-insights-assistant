import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Load environment variables from .env
load_dotenv()

# Build the PostgreSQL connection URL
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

# Locate the source CSV
project_root = Path(__file__).resolve().parents[1]
csv_path = project_root / "data" / "raw" / "customers.csv"

# Read the CSV
df = pd.read_csv(csv_path)

print(f"Loaded {len(df)} customer records from CSV.")

# Basic validation
required_columns = {
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "country",
    "signup_date",
    "status",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

if df["customer_id"].isna().any():
    raise ValueError("customer_id contains missing values.")

if df["customer_id"].duplicated().any():
    raise ValueError("customer_id contains duplicates.")

# Convert signup_date from text to an actual date
df["signup_date"] = pd.to_datetime(
    df["signup_date"],
    errors="raise",
).dt.date

# Insert into PostgreSQL
with engine.begin() as connection:
    connection.execute(
        text(
            """
            INSERT INTO customers (
                customer_id,
                first_name,
                last_name,
                email,
                country,
                signup_date,
                status
            )
            VALUES (
                :customer_id,
                :first_name,
                :last_name,
                :email,
                :country,
                :signup_date,
                :status
            )
            """
        ),
        df.to_dict(orient="records"),
    )

print(f"Inserted {len(df)} customers into PostgreSQL.")