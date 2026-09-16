import pandas as pd


def standardize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names."""
    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return dataframe


def remove_duplicates(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove completely duplicated rows."""
    dataframe = dataframe.copy()

    before = len(dataframe)

    dataframe = dataframe.drop_duplicates()

    after = len(dataframe)

    print(
        f"Removed {before - after} duplicate rows."
    )

    return dataframe


def clean_customers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the customer dataset."""
    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    text_columns = [
        "first_name",
        "last_name",
        "email",
        "country",
        "status",
    ]

    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .astype("string")
                .str.strip()
            )

    if "signup_date" in dataframe.columns:
        dataframe["signup_date"] = pd.to_datetime(
            dataframe["signup_date"],
            errors="coerce",
        )

    return dataframe


def clean_products(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the product dataset."""
    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    text_columns = [
        "product_name",
        "category",
        "status",
    ]

    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .astype("string")
                .str.strip()
            )

    if "price" in dataframe.columns:
        dataframe["price"] = pd.to_numeric(
            dataframe["price"],
            errors="coerce",
        )

    if "stock_quantity" in dataframe.columns:
        dataframe["stock_quantity"] = pd.to_numeric(
            dataframe["stock_quantity"],
            errors="coerce",
        )

    return dataframe


def clean_orders(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the order dataset."""
    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    if "order_date" in dataframe.columns:
        dataframe["order_date"] = pd.to_datetime(
            dataframe["order_date"],
            errors="coerce",
        )

    return dataframe


def clean_order_items(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the order-items dataset."""
    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    numeric_columns = [
        "quantity",
        "unit_price",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

    return dataframe


def clean_transactions(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the transaction dataset."""
    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    numeric_columns = [
        "amount",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

    if "transaction_date" in dataframe.columns:
        dataframe["transaction_date"] = pd.to_datetime(
            dataframe["transaction_date"],
            errors="coerce",
        )

    return dataframe


def clean_events(data: list[dict]) -> list[dict]:
    """Clean behavioral event records."""

    if not data:
        print("No new events to transform.")
        return []

    dataframe = pd.DataFrame(data)

    dataframe = standardize_columns(dataframe)
    dataframe = remove_duplicates(dataframe)

    if "timestamp" in dataframe.columns:
        dataframe["timestamp"] = pd.to_datetime(
            dataframe["timestamp"],
            errors="coerce",
        )

    return dataframe.to_dict(orient="records")


if __name__ == "__main__":
    from pathlib import Path
    import json

    raw_dir = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "raw"
    )

    customers = pd.read_csv(
        raw_dir / "customers.csv"
    )

    products = pd.read_csv(
        raw_dir / "products.csv"
    )

    orders = pd.read_csv(
        raw_dir / "orders.csv"
    )

    order_items = pd.read_csv(
        raw_dir / "order_items.csv"
    )

    transactions = pd.read_csv(
        raw_dir / "transactions.csv"
    )

    with (raw_dir / "events.json").open(
        "r",
        encoding="utf-8",
    ) as file:
        events = json.load(file)

    customers_clean = clean_customers(
        customers
    )

    products_clean = clean_products(
        products
    )

    orders_clean = clean_orders(
        orders
    )

    order_items_clean = clean_order_items(
        order_items
    )

    transactions_clean = clean_transactions(
        transactions
    )

    events_clean = clean_events(
        events
    )

    print("\nTransformation summary:")
    print(
        f"Customers: {len(customers_clean)}"
    )
    print(
        f"Products: {len(products_clean)}"
    )
    print(
        f"Orders: {len(orders_clean)}"
    )
    print(
        f"Order items: {len(order_items_clean)}"
    )
    print(
        f"Transactions: {len(transactions_clean)}"
    )
    print(
        f"Events: {len(events_clean)}"
    )

    print("\nCustomer data types:")
    print(customers_clean.dtypes)

    print("\nProduct data types:")
    print(products_clean.dtypes)