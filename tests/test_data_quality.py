from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/raw")


def test_customers_data_quality():
    df = pd.read_csv(DATA_DIR / "customers.csv")

    assert len(df) == 100
    assert df["customer_id"].notna().all()
    assert df["customer_id"].is_unique


def test_products_data_quality():
    df = pd.read_csv(DATA_DIR / "products.csv")

    assert len(df) == 50
    assert df["product_id"].notna().all()
    assert df["product_id"].is_unique
    assert (df["price"] >= 0).all()
    assert (df["stock_quantity"] >= 0).all()


def test_orders_data_quality():
    df = pd.read_csv(DATA_DIR / "orders.csv")

    assert len(df) == 500
    assert df["order_id"].notna().all()
    assert df["order_id"].is_unique
    assert df["customer_id"].notna().all()

    pd.to_datetime(
        df["order_date"],
        errors="raise",
    )


def test_order_items_data_quality():
    df = pd.read_csv(DATA_DIR / "order_items.csv")

    assert len(df) == 1488
    assert df["order_item_id"].notna().all()
    assert df["order_item_id"].is_unique
    assert df["order_id"].notna().all()
    assert df["product_id"].notna().all()
    assert (df["quantity"] > 0).all()
    assert (df["unit_price"] >= 0).all()


def test_transactions_data_quality():
    df = pd.read_csv(DATA_DIR / "transactions.csv")

    assert len(df) == 500
    assert df["transaction_id"].notna().all()
    assert df["transaction_id"].is_unique
    assert df["order_id"].notna().all()
    assert df["customer_id"].notna().all()
    assert (df["amount"] >= 0).all()

    pd.to_datetime(
        df["transaction_date"],
        errors="raise",
    )