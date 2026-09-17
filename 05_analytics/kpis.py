from pathlib import Path

import pandas as pd


def load_transactions(project_root: Path) -> pd.DataFrame:
    """
    Load the curated transactions dataset.
    """
    curated_dir = project_root / "data" / "curated"

    return pd.read_parquet(
        curated_dir / "transactions.parquet"
    )


def get_completed_transactions(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return transactions with a completed payment status.
    """
    return transactions[
        transactions["status"] == "completed"
    ].copy()


def calculate_payment_success_rate(
    transactions: pd.DataFrame,
) -> float:
    """
    Calculate the percentage of transactions
    with completed payment status.
    """
    if len(transactions) == 0:
        return 0.0

    completed_count = (
        transactions["status"] == "completed"
    ).sum()

    return (completed_count / len(transactions)) * 100


def calculate_completed_revenue(
    transactions: pd.DataFrame,
) -> float:
    """
    Calculate revenue from completed transactions only.
    """
    completed = get_completed_transactions(transactions)

    return completed["amount"].sum()


def calculate_average_order_value(
    transactions: pd.DataFrame,
) -> float:
    """
    Calculate completed revenue divided by
    unique completed orders.
    """
    completed = get_completed_transactions(transactions)

    completed_revenue = completed["amount"].sum()
    completed_orders = completed["order_id"].nunique()

    if completed_orders == 0:
        return 0.0

    return completed_revenue / completed_orders


def calculate_repeat_purchase_rate(
    transactions: pd.DataFrame,
) -> float:
    """
    Calculate the percentage of purchasing customers
    with at least two completed orders.
    """
    completed = get_completed_transactions(transactions)

    customer_orders = (
        completed
        .groupby("customer_id")["order_id"]
        .nunique()
    )

    purchasing_customers = len(customer_orders)

    if purchasing_customers == 0:
        return 0.0

    repeat_customers = (
        customer_orders >= 2
    ).sum()

    return (
        repeat_customers
        / purchasing_customers
        * 100
    )


def calculate_customer_value(
    transactions: pd.DataFrame,
) -> float:
    """
    Calculate average completed revenue per
    purchasing customer during the observed period.
    """
    completed = get_completed_transactions(transactions)

    completed_revenue = completed["amount"].sum()
    purchasing_customers = completed["customer_id"].nunique()

    if purchasing_customers == 0:
        return 0.0

    return completed_revenue / purchasing_customers


def calculate_monthly_revenue_growth(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate monthly completed revenue and
    month-over-month revenue growth.
    """
    completed = get_completed_transactions(transactions)

    monthly_revenue = (
        completed
        .assign(
            month=completed["transaction_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            revenue=("amount", "sum")
        )
    )

    monthly_revenue["month"] = (
        monthly_revenue["month"].astype(str)
    )

    monthly_revenue["revenue_growth_pct"] = (
        monthly_revenue["revenue"]
        .pct_change()
        .mul(100)
    )

    return monthly_revenue


def calculate_all_kpis(
    transactions: pd.DataFrame,
) -> dict:
    """
    Calculate all Week 4 KPIs.
    """
    return {
        "payment_success_rate_pct":
            calculate_payment_success_rate(transactions),

        "completed_revenue":
            calculate_completed_revenue(transactions),

        "average_order_value":
            calculate_average_order_value(transactions),

        "repeat_purchase_rate_pct":
            calculate_repeat_purchase_rate(transactions),

        "customer_value":
            calculate_customer_value(transactions),
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent

    transactions = load_transactions(project_root)

    kpis = calculate_all_kpis(transactions)

    print("Week 4 KPI Summary")
    print("=" * 40)

    print(
        f"Payment Success Rate: "
        f"{kpis['payment_success_rate_pct']:.2f}%"
    )

    print(
        f"Completed Revenue: "
        f"AED {kpis['completed_revenue']:,.2f}"
    )

    print(
        f"Average Order Value: "
        f"AED {kpis['average_order_value']:,.2f}"
    )

    print(
        f"Repeat Purchase Rate: "
        f"{kpis['repeat_purchase_rate_pct']:.2f}%"
    )

    print(
        f"Customer Value: "
        f"AED {kpis['customer_value']:,.2f}"
    )