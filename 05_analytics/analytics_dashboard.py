from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="E-commerce Customer Insights Assistant",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CURATED_DIR = PROJECT_ROOT / "data" / "curated"


# --------------------------------------------------
# Cached data loading
# --------------------------------------------------

@st.cache_data
def load_data():
    """
    Load curated datasets from the Week 3 data pipeline.
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

    events = pd.read_parquet(
        CURATED_DIR / "events.parquet"
    )

    return (
        customers,
        products,
        orders,
        order_items,
        transactions,
        events,
    )


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

(
    customers,
    products,
    orders,
    order_items,
    transactions,
    events,
) = load_data()


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")


# --------------------------------------------------
# Date filter
# --------------------------------------------------

min_date = transactions["transaction_date"].min().date()
max_date = transactions["transaction_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Transaction Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)


# --------------------------------------------------
# Country / region filter
# --------------------------------------------------

countries = sorted(
    customers["country"].dropna().unique().tolist()
)

selected_countries = st.sidebar.multiselect(
    "Country / Region",
    options=countries,
    default=countries,
)


# --------------------------------------------------
# Product category filter
# --------------------------------------------------

categories = sorted(
    products["category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=categories,
    default=categories,
)


# --------------------------------------------------
# Validate date selection
# --------------------------------------------------

if len(selected_dates) != 2:

    st.warning(
        "Please select both a start date and an end date."
    )

    st.stop()


start_date, end_date = selected_dates


# --------------------------------------------------
# Filter customers by country
# --------------------------------------------------

selected_customer_ids = customers[
    customers["country"].isin(selected_countries)
]["customer_id"]


# --------------------------------------------------
# Filter products by category
# --------------------------------------------------

selected_product_ids = products[
    products["category"].isin(selected_categories)
]["product_id"]


# --------------------------------------------------
# Build category-filtered orders
# --------------------------------------------------

category_order_ids = order_items[
    order_items["product_id"].isin(
        selected_product_ids
    )
]["order_id"].unique()


# --------------------------------------------------
# Filter transactions
# --------------------------------------------------

filtered_transactions = transactions[
    transactions["transaction_date"].dt.date.between(
        start_date,
        end_date,
    )
    &
    transactions["customer_id"].isin(
        selected_customer_ids
    )
    &
    transactions["order_id"].isin(
        category_order_ids
    )
].copy()


# --------------------------------------------------
# Filter order items
# --------------------------------------------------

filtered_order_items = order_items[
    order_items["product_id"].isin(
        selected_product_ids
    )
    &
    order_items["order_id"].isin(
        filtered_transactions["order_id"]
    )
].copy()


# --------------------------------------------------
# Filter orders
# --------------------------------------------------

filtered_order_ids = filtered_transactions[
    "order_id"
].unique()

filtered_orders = orders[
    orders["order_id"].isin(
        filtered_order_ids
    )
].copy()


# --------------------------------------------------
# Filter events
# --------------------------------------------------

filtered_events = events[
    events["customer_id"].isin(
        filtered_transactions["customer_id"].unique()
    )
    &
    events["timestamp"].dt.date.between(
        start_date,
        end_date,
    )
].copy()


# --------------------------------------------------
# KPI calculations
# --------------------------------------------------

completed_transactions = filtered_transactions[
    filtered_transactions["status"] == "completed"
].copy()


# Completed revenue

completed_revenue = completed_transactions[
    "amount"
].sum()


# Completed orders

completed_orders = completed_transactions[
    "order_id"
].nunique()


# Average order value

if completed_orders > 0:

    average_order_value = (
        completed_revenue
        / completed_orders
    )

else:

    average_order_value = 0.0


# Purchasing customers

purchasing_customers = completed_transactions[
    "customer_id"
].nunique()


# Repeat purchase rate and customer value

if purchasing_customers > 0:

    customer_order_counts = (
        completed_transactions
        .groupby("customer_id")["order_id"]
        .nunique()
    )

    repeat_customers = (
        customer_order_counts >= 2
    ).sum()

    repeat_purchase_rate = (
        repeat_customers
        / purchasing_customers
        * 100
    )

    customer_value = (
        completed_revenue
        / purchasing_customers
    )

else:

    repeat_purchase_rate = 0.0
    customer_value = 0.0


# Payment success rate

total_transactions = len(filtered_transactions)

if total_transactions > 0:

    payment_success_rate = (
        len(completed_transactions)
        / total_transactions
        * 100
    )

else:

    payment_success_rate = 0.0


# --------------------------------------------------
# Monthly revenue calculation
# --------------------------------------------------

monthly_revenue = (
    completed_transactions
    .assign(
        month=completed_transactions[
            "transaction_date"
        ].dt.to_period("M")
    )
    .groupby("month", as_index=False)
    .agg(
        revenue=("amount", "sum")
    )
)

monthly_revenue["month"] = (
    monthly_revenue["month"].astype(str)
)


# --------------------------------------------------
# Revenue by product category
# --------------------------------------------------

category_revenue = (
    filtered_order_items
    .merge(
        products[["product_id", "category"]],
        on="product_id",
        how="left",
    )
    .assign(
        revenue=lambda df:
            df["quantity"] * df["unit_price"]
    )
    .groupby("category", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        units_sold=("quantity", "sum"),
    )
    .sort_values(
        "revenue",
        ascending=True,
    )
)


# --------------------------------------------------
# Order status distribution
# --------------------------------------------------

order_status_counts = (
    filtered_orders["status"]
    .value_counts()
    .rename_axis("status")
    .reset_index(
        name="order_count"
    )
)


# --------------------------------------------------
# Customer activity distribution
# --------------------------------------------------

customer_activity = (
    filtered_events
    .groupby("customer_id")
    .agg(
        event_count=("event_id", "count")
    )
    .reset_index()
)


# --------------------------------------------------
# Transaction amount data
# --------------------------------------------------

filtered_transaction_amounts = (
    filtered_transactions["amount"]
    .dropna()
)


# --------------------------------------------------
# Dashboard header
# --------------------------------------------------

st.title(
    "📊 E-commerce Customer Insights Assistant"
)

st.markdown(
    """
    **Analytics Dashboard**

    Explore customer activity, orders, transactions,
    product performance, and business KPIs using the
    curated data produced by the data engineering pipeline.
    """
)


# --------------------------------------------------
# Active filter summary
# --------------------------------------------------

st.subheader("Active Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    st.metric(
        "Start Date",
        start_date.strftime("%Y-%m-%d"),
    )


with filter_col2:

    st.metric(
        "End Date",
        end_date.strftime("%Y-%m-%d"),
    )


with filter_col3:

    st.metric(
        "Selected Countries",
        len(selected_countries),
    )


# --------------------------------------------------
# KPI cards
# --------------------------------------------------

st.subheader("Business KPIs")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)


with kpi_col1:

    st.metric(
        "Completed Revenue",
        f"AED {completed_revenue:,.2f}",
    )


with kpi_col2:

    st.metric(
        "Average Order Value",
        f"AED {average_order_value:,.2f}",
    )


with kpi_col3:

    st.metric(
        "Repeat Purchase Rate",
        f"{repeat_purchase_rate:.2f}%",
    )


with kpi_col4:

    st.metric(
        "Customer Value",
        f"AED {customer_value:,.2f}",
    )


with kpi_col5:

    st.metric(
        "Payment Success Rate",
        f"{payment_success_rate:.2f}%",
    )


# --------------------------------------------------
# Filtered data overview
# --------------------------------------------------

st.subheader("Filtered Data Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Transactions",
        f"{len(filtered_transactions):,}",
    )


with col2:

    st.metric(
        "Order Items",
        f"{len(filtered_order_items):,}",
    )


with col3:

    st.metric(
        "Customers",
        f"{filtered_transactions['customer_id'].nunique():,}",
    )


with col4:

    st.metric(
        "Products",
        f"{filtered_order_items['product_id'].nunique():,}",
    )


# ==================================================
# ANALYTICAL VISUALIZATIONS
# ==================================================


# --------------------------------------------------
# Monthly revenue trend
# --------------------------------------------------

st.subheader("Monthly Revenue Trend")

if monthly_revenue.empty:

    st.info(
        "No revenue data is available "
        "for the selected filters."
    )

else:

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        monthly_revenue["month"],
        monthly_revenue["revenue"],
        marker="o",
        linewidth=2,
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Completed Revenue (AED)")
    ax.set_title(
        "Monthly Completed Revenue",
        fontsize=14,
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


# --------------------------------------------------
# Revenue by product category
# --------------------------------------------------

st.subheader("Revenue by Product Category")

if category_revenue.empty:

    st.info(
        "No category revenue is available "
        "for the selected filters."
    )

else:

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.barh(
        category_revenue["category"],
        category_revenue["revenue"],
    )

    ax.set_xlabel("Revenue (AED)")
    ax.set_ylabel("Product Category")
    ax.set_title(
        "Revenue by Product Category",
        fontsize=14,
    )

    for index, value in enumerate(
        category_revenue["revenue"]
    ):

        ax.text(
            value,
            index,
            f" AED {value:,.0f}",
            va="center",
            fontsize=9,
        )

    ax.grid(
        axis="x",
        alpha=0.3,
    )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


# --------------------------------------------------
# Order status distribution
# --------------------------------------------------

st.subheader("Order Status Distribution")

if order_status_counts.empty:

    st.info(
        "No order status data is available "
        "for the selected filters."
    )

else:

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(
        order_status_counts["status"],
        order_status_counts["order_count"],
    )

    ax.set_xlabel("Order Status")
    ax.set_ylabel("Number of Orders")
    ax.set_title(
        "Order Status Distribution",
        fontsize=14,
    )

    for bar in bars:

        value = bar.get_height()

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            value,
            f"{int(value)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


# --------------------------------------------------
# Customer activity distribution
# --------------------------------------------------

st.subheader("Customer Activity Distribution")

if customer_activity.empty:

    st.info(
        "No customer activity data is available "
        "for the selected filters."
    )

else:

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        customer_activity["event_count"],
        bins=10,
    )

    median_activity = (
        customer_activity["event_count"].median()
    )

    ax.axvline(
        median_activity,
        linestyle="--",
        linewidth=2,
        label=(
            f"Median: "
            f"{median_activity:.0f} events"
        ),
    )

    ax.set_xlabel(
        "Recorded Events per Customer"
    )

    ax.set_ylabel(
        "Number of Customers"
    )

    ax.set_title(
        "Distribution of Customer Activity",
        fontsize=14,
    )

    ax.legend()

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


# --------------------------------------------------
# Transaction amount distribution
# --------------------------------------------------

st.subheader("Transaction Amount Distribution")

if filtered_transaction_amounts.empty:

    st.info(
        "No transaction amount data is available "
        "for the selected filters."
    )

else:

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        filtered_transaction_amounts,
        bins=20,
    )

    transaction_mean = (
        filtered_transaction_amounts.mean()
    )

    transaction_median = (
        filtered_transaction_amounts.median()
    )

    ax.axvline(
        transaction_mean,
        linestyle="--",
        linewidth=2,
        label=(
            f"Mean: "
            f"AED {transaction_mean:,.0f}"
        ),
    )

    ax.axvline(
        transaction_median,
        linestyle=":",
        linewidth=2,
        label=(
            f"Median: "
            f"AED {transaction_median:,.0f}"
        ),
    )

    ax.set_xlabel(
        "Transaction Amount (AED)"
    )

    ax.set_ylabel(
        "Number of Transactions"
    )

    ax.set_title(
        "Distribution of Transaction Amounts",
        fontsize=14,
    )

    ax.legend()

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    st.caption(
        "The distribution shows transaction frequency "
        "across amount ranges. Mean and median are shown "
        "for comparison."
    )

    plt.close(fig)


# --------------------------------------------------
# Data status
# --------------------------------------------------

st.success(
    "Curated datasets loaded and dashboard "
    "filters applied successfully."
)