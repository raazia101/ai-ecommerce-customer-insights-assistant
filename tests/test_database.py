import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()


def get_database_engine():
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")

    url = (
        f"postgresql+psycopg://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    return create_engine(url)


def test_table_row_counts():
    engine = get_database_engine()

    expected_counts = {
        "customers": 100,
        "products": 50,
        "orders": 500,
        "order_items": 1488,
        "transactions": 500,
    }

    with engine.connect() as connection:
        for table, expected_count in expected_counts.items():
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )
            actual_count = result.scalar()

            assert actual_count == expected_count


def test_orders_have_valid_customers():
    engine = get_database_engine()

    query = text("""
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """)

    with engine.connect() as connection:
        invalid_count = connection.execute(query).scalar()

    assert invalid_count == 0


def test_order_items_have_valid_orders():
    engine = get_database_engine()

    query = text("""
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """)

    with engine.connect() as connection:
        invalid_count = connection.execute(query).scalar()

    assert invalid_count == 0


def test_order_items_have_valid_products():
    engine = get_database_engine()

    query = text("""
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL
    """)

    with engine.connect() as connection:
        invalid_count = connection.execute(query).scalar()

    assert invalid_count == 0


def test_transactions_have_valid_orders():
    engine = get_database_engine()

    query = text("""
        SELECT COUNT(*)
        FROM transactions t
        LEFT JOIN orders o
            ON t.order_id = o.order_id
        WHERE o.order_id IS NULL
    """)

    with engine.connect() as connection:
        invalid_count = connection.execute(query).scalar()

    assert invalid_count == 0


def test_transactions_have_valid_customers():
    engine = get_database_engine()

    query = text("""
        SELECT COUNT(*)
        FROM transactions t
        LEFT JOIN customers c
            ON t.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """)

    with engine.connect() as connection:
        invalid_count = connection.execute(query).scalar()

    assert invalid_count == 0