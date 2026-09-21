# Week 5 — ML Feature Audit

## Dataset

The machine learning feature dataset was generated from the curated
Parquet datasets produced by the Week 3 ETL pipeline.

Output:

`data/curated/ml_customer_features.parquet`

## Dataset Size

- Rows: 84
- Columns: 24
- Unique customers: 84
- Duplicate customer IDs: 0

Each row represents one eligible customer at the prediction cutoff.

## Target Distribution

The target variable is `repeat_purchase`.

- Class 0: 51 customers
- Class 1: 33 customers
- Class 0 percentage: 60.71%
- Class 1 percentage: 39.29%

The distribution is moderately imbalanced but does not exhibit the extreme imbalance observed with the 30-day prediction window.

## Missing Values

Missing values occur only in:

- `last_purchase_date`: 10
- `days_since_last_purchase`: 10

These missing values correspond to the 10 customers who had no previous
completed purchase before the prediction cutoff.

The missing values therefore represent a meaningful business condition
rather than a data-quality failure.

The feature `has_previous_purchase` explicitly represents this condition.

## Categorical Features

### Country

- UK: 22
- India: 20
- UAE: 19
- Canada: 12
- USA: 11

### Customer Status

- active: 59
- inactive: 25

Both categorical variables contain multiple values and can therefore
provide usable information to a classification model.

## Numerical Features

The numerical feature set contains customer tenure, historical
transaction behaviour, purchasing behaviour, product behaviour, and
customer engagement behaviour.

No numerical feature has zero variance.

## Selected Predictive Features

The following features will be considered for the initial model:

### Customer

- `country`
- `status`
- `customer_tenure_days`

### Transaction Behaviour

- `completed_order_count`
- `completed_revenue`
- `average_order_value`
- `days_since_last_purchase`
- `has_previous_purchase`
- `total_transaction_count`
- `failed_transaction_count`
- `refunded_transaction_count`

### Product Behaviour

- `unique_products_purchased`
- `unique_categories_purchased`

### Engagement Behaviour

- `total_event_count`
- `product_view_count`
- `add_to_cart_count`
- `checkout_started_count`
- `search_count`
- `login_count`
- `purchase_count`
- `remove_from_cart_count`

## Excluded Columns

### `customer_id`

Excluded because it is an identifier and does not represent customer
behaviour.

### `last_purchase_date`

Excluded from the initial model because its useful information has
already been represented through `days_since_last_purchase`.

### `repeat_purchase`

Excluded from the feature set because it is the target variable.

## Initial Model

The first baseline model will be Logistic Regression.

Logistic Regression is suitable for establishing a simple binary
classification baseline and provides predicted probabilities for the
future purchase outcome.

Because the dataset contains only 84 observations, model complexity
will be kept relatively low to reduce overfitting.

## Evaluation

The model will be evaluated using stratified cross-validation.

The following metrics will be considered:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

Accuracy will not be used as the only evaluation metric.

## Dataset Limitation

The dataset contains only 84 eligible customers. Therefore, evaluation
results may have substantial variance and should not be interpreted as
evidence of production-level model performance.

The purpose of the Week 5 model is to demonstrate a leakage-aware
supervised machine learning workflow using the curated internship
dataset.