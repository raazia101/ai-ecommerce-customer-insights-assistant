from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CURATED_DIR = BASE_DIR / "data" / "curated"
VALIDATION_LOG = BASE_DIR / "data" / "validation_log.csv"


def log_validation(
    check_name: str,
    dataset_name: str,
    status: str,
) -> None:
    """Append a validation result to the validation log."""

    log_entry = pd.DataFrame(
        [
            {
                "timestamp": datetime.now().isoformat(),
                "check": check_name,
                "dataset": dataset_name,
                "status": status,
            }
        ]
    )

    if VALIDATION_LOG.exists():
        log_entry.to_csv(
            VALIDATION_LOG,
            mode="a",
            header=False,
            index=False,
        )
    else:
        log_entry.to_csv(
            VALIDATION_LOG,
            index=False,
        )


def check_schema(
    dataframe: pd.DataFrame,
    expected_columns: list[str],
    dataset_name: str,
) -> bool:
    """Check that a dataset contains the expected columns."""

    actual_columns = list(dataframe.columns)

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    if missing_columns:
        print(
            f"[FAIL] {dataset_name} schema: "
            f"missing {missing_columns}"
        )

        log_validation(
            "schema",
            dataset_name,
            "FAIL",
        )

        return False

    print(f"[PASS] {dataset_name} schema")

    log_validation(
        "schema",
        dataset_name,
        "PASS",
    )

    return True


def check_completeness(
    dataframe: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> bool:
    """Check that required columns contain no null values."""

    missing_values = dataframe[required_columns].isnull().sum()

    failed_columns = missing_values[
        missing_values > 0
    ]

    if not failed_columns.empty:
        print(
            f"[FAIL] {dataset_name} completeness: "
            f"{failed_columns.to_dict()}"
        )

        log_validation(
            "completeness",
            dataset_name,
            "FAIL",
        )

        return False

    print(f"[PASS] {dataset_name} completeness")

    log_validation(
        "completeness",
        dataset_name,
        "PASS",
    )

    return True


def check_uniqueness(
    dataframe: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> bool:
    """Check that a column contains unique values."""

    duplicate_count = dataframe[column].duplicated().sum()

    if duplicate_count > 0:
        print(
            f"[FAIL] {dataset_name} uniqueness: "
            f"{duplicate_count} duplicates"
        )

        log_validation(
            "uniqueness",
            dataset_name,
            "FAIL",
        )

        return False

    print(f"[PASS] {dataset_name} uniqueness")

    log_validation(
        "uniqueness",
        dataset_name,
        "PASS",
    )

    return True


def check_non_negative(
    dataframe: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> bool:
    """Check that numeric values are not negative."""

    invalid_count = (dataframe[column] < 0).sum()

    if invalid_count > 0:
        print(
            f"[FAIL] {dataset_name} range: "
            f"{invalid_count} negative values in {column}"
        )

        log_validation(
            f"range_{column}",
            dataset_name,
            "FAIL",
        )

        return False

    print(
        f"[PASS] {dataset_name} range: "
        f"{column}"
    )

    log_validation(
        f"range_{column}",
        dataset_name,
        "PASS",
    )

    return True


def check_positive(
    dataframe: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> bool:
    """Check that numeric values are greater than zero."""

    invalid_count = (dataframe[column] <= 0).sum()

    if invalid_count > 0:
        print(
            f"[FAIL] {dataset_name} range: "
            f"{invalid_count} non-positive values in {column}"
        )

        log_validation(
            f"positive_{column}",
            dataset_name,
            "FAIL",
        )

        return False

    print(
        f"[PASS] {dataset_name} range: "
        f"{column}"
    )

    log_validation(
        f"positive_{column}",
        dataset_name,
        "PASS",
    )

    return True


def check_referential_integrity(
    child_dataframe: pd.DataFrame,
    child_column: str,
    parent_dataframe: pd.DataFrame,
    parent_column: str,
    relationship_name: str,
) -> bool:
    """Check that every child key exists in the parent dataset."""

    child_values = set(
        child_dataframe[child_column].dropna()
    )

    parent_values = set(
        parent_dataframe[parent_column].dropna()
    )

    orphan_values = child_values - parent_values

    if orphan_values:
        print(
            f"[FAIL] {relationship_name}: "
            f"{len(orphan_values)} orphan values"
        )

        log_validation(
            "referential_integrity",
            relationship_name,
            "FAIL",
        )

        return False

    print(
        f"[PASS] {relationship_name}"
    )

    log_validation(
        "referential_integrity",
        relationship_name,
        "PASS",
    )

    return True


def run_validations() -> bool:
    """
    Run all data-quality checks.

    Returns True when every validation passes.
    Returns False when at least one validation fails.
    """

    customers = pd.read_parquet(
        CURATED_DIR / "customers.parquet"
    )

    products = pd.read_parquet(
        CURATED_DIR / "products.parquet"
    )

    orders = pd.read_parquet(
        CURATED_DIR / "orders.parquet"
    )

    order_items = pd.read_parquet(
        CURATED_DIR / "order_items.parquet"
    )

    transactions = pd.read_parquet(
        CURATED_DIR / "transactions.parquet"
    )

    results = []

    print("Running validation checks...\n")

    # Customer checks

    results.append(
        check_schema(
            customers,
            [
                "customer_id",
                "first_name",
                "last_name",
                "email",
                "country",
                "signup_date",
                "status",
            ],
            "customers",
        )
    )

    results.append(
        check_completeness(
            customers,
            [
                "customer_id",
                "email",
                "country",
            ],
            "customers",
        )
    )

    results.append(
        check_uniqueness(
            customers,
            "customer_id",
            "customers",
        )
    )

    # Range checks

    print("\nRange checks:")

    results.append(
        check_non_negative(
            products,
            "price",
            "products",
        )
    )

    results.append(
        check_non_negative(
            products,
            "stock_quantity",
            "products",
        )
    )

    results.append(
        check_positive(
            order_items,
            "quantity",
            "order_items",
        )
    )

    results.append(
        check_non_negative(
            order_items,
            "unit_price",
            "order_items",
        )
    )

    results.append(
        check_non_negative(
            transactions,
            "amount",
            "transactions",
        )
    )

    # Referential integrity checks

    print("\nReferential integrity checks:")

    results.append(
        check_referential_integrity(
            orders,
            "customer_id",
            customers,
            "customer_id",
            "orders.customer_id -> customers.customer_id",
        )
    )

    results.append(
        check_referential_integrity(
            order_items,
            "order_id",
            orders,
            "order_id",
            "order_items.order_id -> orders.order_id",
        )
    )

    results.append(
        check_referential_integrity(
            order_items,
            "product_id",
            products,
            "product_id",
            "order_items.product_id -> products.product_id",
        )
    )

    results.append(
        check_referential_integrity(
            transactions,
            "customer_id",
            customers,
            "customer_id",
            "transactions.customer_id -> customers.customer_id",
        )
    )

    results.append(
        check_referential_integrity(
            transactions,
            "order_id",
            orders,
            "order_id",
            "transactions.order_id -> orders.order_id",
        )
    )

    all_passed = all(results)

    print("\nValidation completed.")

    if all_passed:
        print("Validation result: PASS")
    else:
        print("Validation result: FAIL")

    return all_passed


if __name__ == "__main__":
    run_validations()