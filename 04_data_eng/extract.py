import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
STATE_FILE = BASE_DIR / "data" / "pipeline_state.json"


def extract_csv(filename: str) -> pd.DataFrame:
    """Extract a CSV file into a pandas DataFrame."""

    path = RAW_DIR / filename

    dataframe = pd.read_csv(path)

    print(
        f"Extracted {filename}: "
        f"{len(dataframe)} rows"
    )

    return dataframe


def extract_json(filename: str) -> list[dict]:
    """Extract a JSON file into a list of dictionaries."""

    path = RAW_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print(
        f"Extracted {filename}: "
        f"{len(data)} records"
    )

    return data


def get_watermark() -> datetime | None:
    """Read the last successfully processed event timestamp."""

    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        state = json.load(file)

    watermark = state.get("events_watermark")

    if watermark is None:
        return None

    return datetime.fromisoformat(watermark)


def save_watermark(timestamp: datetime) -> None:
    """Save the latest successfully processed event timestamp."""

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    state = {
        "events_watermark": timestamp.isoformat()
    }

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=4,
        )


def extract_incremental_events() -> list[dict]:
    """Extract only events newer than the stored watermark."""

    events = extract_json("events.json")

    dataframe = pd.DataFrame(events)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    watermark = get_watermark()

    if watermark is not None:
        new_events = dataframe[
            dataframe["timestamp"] > watermark
        ]
    else:
        new_events = dataframe

    print(
        f"Incremental events extracted: "
        f"{len(new_events)}"
    )

    return new_events.to_dict(
        orient="records"
    )


def main() -> None:
    """Test extraction from the project's raw data files."""

    customers = extract_csv("customers.csv")
    products = extract_csv("products.csv")
    orders = extract_csv("orders.csv")
    order_items = extract_csv("order_items.csv")
    transactions = extract_csv("transactions.csv")
    events = extract_json("events.json")

    print("\nExtraction summary:")
    print(f"Customers: {len(customers)}")
    print(f"Products: {len(products)}")
    print(f"Orders: {len(orders)}")
    print(f"Order items: {len(order_items)}")
    print(f"Transactions: {len(transactions)}")
    print(f"Events: {len(events)}")


if __name__ == "__main__":
    main()