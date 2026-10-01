from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

FEATURE_PATH = (
    BASE_DIR
    / "data"
    / "curated"
    / "ml_customer_features.parquet"
)

REFERENCE_PATH = FEATURE_PATH
CURRENT_PATH = FEATURE_PATH

NUMERICAL_FEATURES = [
    "customer_tenure_days",
    "completed_order_count",
    "completed_revenue",
    "average_order_value",
    "days_since_last_purchase",
    "has_previous_purchase",
    "total_transaction_count",
    "failed_transaction_count",
    "refunded_transaction_count",
    "unique_products_purchased",
    "unique_categories_purchased",
    "total_event_count",
    "product_view_count",
    "add_to_cart_count",
    "checkout_started_count",
    "search_count",
    "login_count",
    "purchase_count",
    "remove_from_cart_count",
]

CATEGORICAL_FEATURES = [
    "country",
    "status",
]


def numerical_drift(reference, current):
    results = []

    for feature in NUMERICAL_FEATURES:
        reference_mean = reference[feature].mean()
        current_mean = current[feature].mean()

        reference_std = reference[feature].std()
        current_std = current[feature].std()

        mean_difference = current_mean - reference_mean

        if reference_mean != 0:
            mean_change_pct = (
                mean_difference / abs(reference_mean)
            ) * 100
        else:
            mean_change_pct = 0.0

        results.append(
            {
                "feature": feature,
                "reference_mean": reference_mean,
                "current_mean": current_mean,
                "mean_change_pct": mean_change_pct,
                "reference_std": reference_std,
                "current_std": current_std,
            }
        )

    return pd.DataFrame(results)


def categorical_drift(reference, current):
    results = []

    for feature in CATEGORICAL_FEATURES:
        reference_distribution = (
            reference[feature]
            .value_counts(normalize=True)
        )

        current_distribution = (
            current[feature]
            .value_counts(normalize=True)
        )

        categories = set(reference_distribution.index) | set(
            current_distribution.index
        )

        for category in sorted(categories):
            reference_pct = reference_distribution.get(
                category,
                0.0,
            )

            current_pct = current_distribution.get(
                category,
                0.0,
            )

            results.append(
                {
                    "feature": feature,
                    "category": category,
                    "reference_proportion": reference_pct,
                    "current_proportion": current_pct,
                    "difference": current_pct - reference_pct,
                }
            )

    return pd.DataFrame(results)


def main():
    print("Feature drift monitoring")
    print("------------------------")

    reference = pd.read_parquet(REFERENCE_PATH)
    current = pd.read_parquet(CURRENT_PATH)

    print(f"Reference rows: {len(reference)}")
    print(f"Current rows:   {len(current)}")

    numerical_results = numerical_drift(
        reference,
        current,
    )

    categorical_results = categorical_drift(
        reference,
        current,
    )

    print("\nNumerical feature comparison:")
    print(
        numerical_results[
            [
                "feature",
                "reference_mean",
                "current_mean",
                "mean_change_pct",
            ]
        ].to_string(index=False)
    )

    print("\nCategorical feature comparison:")
    print(
        categorical_results.to_string(index=False)
    )

    print(
        "\nMonitoring note:"
        "\nReference and current datasets are currently "
        "the same dataset."
        "\nTherefore, this run establishes a baseline "
        "and does not demonstrate production drift."
    )


if __name__ == "__main__":
    main()