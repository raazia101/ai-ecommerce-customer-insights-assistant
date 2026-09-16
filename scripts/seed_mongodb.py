import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient


# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "intern_db")


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"


def load_json(path: Path) -> list[dict]:
    """Load a JSON file and return a list of documents."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_csv(path: Path) -> list[dict]:
    """Load a CSV file and return a list of documents."""
    dataframe = pd.read_csv(path)
    return dataframe.to_dict(orient="records")


def seed_collection(
    collection,
    documents: list[dict],
) -> None:
    """Replace existing collection data with the supplied documents."""
    collection.delete_many({})

    if documents:
        collection.insert_many(documents)

    print(
        f"Seeded {collection.name}: "
        f"{collection.count_documents({})} documents"
    )


def main() -> None:
    """Seed MongoDB with customers, products and behavioral events."""

    client = MongoClient(MONGO_URI)

    # Verify the connection
    client.admin.command("ping")
    print("MongoDB connection successful.")

    database = client[MONGO_DB]

    customers = load_csv(DATA_DIR / "customers.csv")
    products = load_csv(DATA_DIR / "products.csv")
    events = load_json(DATA_DIR / "events.json")

    seed_collection(
        database["customers"],
        customers,
    )

    seed_collection(
        database["products"],
        products,
    )

    seed_collection(
        database["events"],
        events,
    )

    client.close()
    print("MongoDB seeding complete.")


if __name__ == "__main__":
    main()