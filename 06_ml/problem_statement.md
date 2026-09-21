# Week 5 — Machine Learning Problem Statement

## Objective

The objective of the Week 5 machine learning task is to predict whether an eligible customer will make at least one completed purchase during a future 90-day prediction window.

The prediction is made at the customer level using historical customer, transaction, order, product, and event behaviour.

## Prediction Cutoff

The prediction cutoff is:

2026-05-24 00:00:00

Only information available on or before this timestamp may be used to construct model features.

## Prediction Window

The future prediction window is:

2026-05-24 00:00:00 < timestamp <= 2026-08-22 00:00:00

Customer behaviour during this period is used only to construct the target variable.

## Target Variable

The target variable is:

`repeat_purchase`

Definition:

- `1` if the customer has at least one transaction with `status = 'completed'` during the 90-day prediction window.
- `0` otherwise.

The transaction dataset is used for this definition because it explicitly contains the `completed` status.

## Customer Eligibility

A customer is eligible for prediction if:

`signup_date <= 2026-05-24 00:00:00`

This prevents customers who had not yet joined the platform at the prediction cutoff from entering the prediction dataset.

## Dataset Distribution

Using the curated Week 3 Parquet datasets:

- Total customers: 100
- Eligible customers: 84
- Positive customers: 33
- Negative customers: 51
- Positive rate: 39.29%
- Future completed transactions: 46

## Candidate Features

Candidate features will be constructed exclusively from historical information available at the prediction cutoff.

### Transaction Features

- completed_order_count
- completed_revenue
- average_order_value
- days_since_last_purchase
- total_transaction_count
- failed_transaction_count
- refunded_transaction_count

### Event Features

- total_event_count
- product_view_count
- add_to_cart_count
- checkout_started_count
- search_count
- login_count
- purchase_event_count
- remove_from_cart_count

### Customer Features

- country
- customer status
- customer_tenure_days

### Product Behaviour Features

Potential derived features include:

- unique_products_purchased
- unique_categories_purchased

These will be calculated only from historical purchases.

## Unit of Analysis

The unit of analysis is one customer at the prediction cutoff.

Each row in the final machine learning dataset represents one eligible customer and contains:

1. Historical features available at the prediction cutoff.
2. A binary future purchase target.

## Data Sources

The ML features will be derived from the curated datasets produced by the Week 3 ETL pipeline:

- customers.parquet
- events.parquet
- orders.parquet
- order_items.parquet
- products.parquet
- transactions.parquet

## ML Task Type

This is a supervised binary classification problem.

The model predicts:

`repeat_purchase ∈ {0, 1}`

The first model should establish a simple baseline before more complex models are considered.

## Important Limitation

The dataset contains only 84 eligible customers. Therefore, model complexity and evaluation must be appropriate for a small dataset.

Model performance should not be interpreted as evidence of production-level predictive performance.