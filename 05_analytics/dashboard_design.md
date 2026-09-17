# Analytics Dashboard Design

## 1. Purpose

The Analytics Dashboard is the interactive business-facing component of the E-commerce Customer Insights Assistant.

It converts the curated datasets produced by the Week 3 data engineering pipeline into interactive business metrics and analytical visualizations.

The dashboard allows users to explore:

- Transaction performance
- Revenue trends
- Customer purchasing behavior
- Customer activity
- Product-category performance
- Order status distribution
- Transaction value distribution

The dashboard is implemented using Streamlit and reads from the curated Parquet layer rather than directly from the raw source data.

---

## 2. Data Source

The dashboard reads curated datasets from:

    data/curated/

The following datasets are used:

- `customers.parquet`
- `products.parquet`
- `orders.parquet`
- `order_items.parquet`
- `transactions.parquet`
- `events.parquet`

The dashboard does not directly read the original raw CSV or JSON files.

This maintains separation between the data ingestion layer and the analytics presentation layer.

The Week 3 pipeline is responsible for producing validated curated datasets, while the Week 4 dashboard consumes those curated outputs.

---

## 3. Dashboard Architecture

The dashboard follows the following data flow:

    Week 3 Data Pipeline
            |
            v
    Curated Parquet Data
            |
            v
    Streamlit Data Loading
            |
            v
    Interactive Filters
            |
            v
    Filtered Data
            |
            +--------------------+
            |                    |
            v                    v
        KPI Engine        Visualization Layer
            |                    |
            v                    v
      Business KPIs       Analytical Charts

The dashboard uses a cached data-loading function so that the curated datasets do not need to be unnecessarily re-read from disk during every Streamlit interaction.

The main implementation is contained in:

    05_analytics/analytics_dashboard.py

---

## 4. Technologies Used

The dashboard uses the following technologies:

- Python
- Pandas
- Matplotlib
- Streamlit
- Parquet
- Streamlit `st.cache_data`

### Pandas

Pandas is used for:

- Loading Parquet datasets
- Filtering data
- Joining related datasets
- Aggregating metrics
- Calculating KPIs
- Preparing chart data

### Matplotlib

Matplotlib is used to create the dashboard visualizations.

It provides control over:

- Chart titles
- Axis labels
- Data annotations
- Grid lines
- Reference lines
- Figure sizing

### Streamlit

Streamlit provides the interactive dashboard interface.

It is responsible for:

- Sidebar filters
- KPI cards
- Layout
- Charts
- Informational messages
- Dashboard state updates

### Parquet

Parquet is used as the analytics data format because the Week 3 pipeline produces curated Parquet datasets.

---

## 5. Data Loading

The dashboard loads all required curated datasets through a cached function.

Conceptually, the implementation follows:

    @st.cache_data
    def load_data():
        ...
        return customers, products, orders, order_items, transactions, events

Caching prevents unnecessary repeated file reads when users interact with the dashboard.

The dashboard therefore treats the curated Parquet layer as its primary analytics source.

---

## 6. Interactive Filters

The dashboard provides three main filtering mechanisms.

### 6.1 Transaction Date Filter

Users can select a start date and end date.

Transaction filtering is performed using:

    transactions.transaction_date

Event filtering is performed using:

    events.timestamp

This ensures that customer activity shown on the dashboard also respects the selected observation period.

The date filter affects the relevant transaction, order-item, order, customer, and event outputs.

---

### 6.2 Country / Region Filter

The dashboard provides a geographic filter using the `country` field from the customer dataset.

The current dataset does not contain a separate `region` field.

Therefore, country is used as the available geographic segmentation.

The filtering relationship is:

    Selected Countries
            |
            v
       Customer IDs
            |
            v
       Transactions
            |
            v
     Dashboard Metrics

This allows users to examine transaction and customer metrics for selected customer countries.

---

### 6.3 Product Category Filter

Users can select one or more product categories.

The filtering relationship is:

    Product Category
            |
            v
        Product IDs
            |
            v
        Order Items
            |
            v
         Order IDs
            |
            v
       Transactions

This allows the dashboard to restrict the analytical population to orders associated with selected product categories.

---

## 7. Filtered Data Relationships

The dashboard uses relationships between the curated datasets to propagate filter selections.

### Customer-based filtering

    Country
       |
       v
    Customer IDs
       |
       v
    Transactions
       |
       +----> KPIs
       |
       +----> Orders
       |
       +----> Order Items
       |
       +----> Customer Events

### Product-category filtering

    Product Category
          |
          v
      Product IDs
          |
          v
      Order Items
          |
          v
       Order IDs
          |
          v
      Transactions

### Date filtering

Transaction-level calculations use the transaction date.

Customer activity calculations use the event timestamp.

This distinction is important because events and transactions represent different types of time-based records.

---

# 8. Business KPIs

The dashboard displays five primary business KPIs.

## 8.1 Completed Revenue

### Definition

Completed Revenue is the sum of transaction amounts for transactions whose status is `completed`.

### Formula

    Completed Revenue =
    SUM(amount where status = completed)

Failed transactions and refunded transactions are excluded from this KPI.

The Week 4 validated full-dataset result is:

    AED 431,177.98

---

## 8.2 Average Order Value

### Definition

Average Order Value (AOV) represents the average completed revenue per unique completed order.

### Formula

    AOV =
    Completed Revenue / Unique Completed Orders

The Week 4 validated full-dataset result is:

    AED 1,497.15

---

## 8.3 Repeat Purchase Rate

### Definition

Repeat Purchase Rate is the percentage of purchasing customers who completed at least two unique orders during the selected observation period.

### Formula

    Repeat Purchase Rate =
    Repeat Customers / Purchasing Customers × 100

For the full dataset:

- Purchasing customers = 94
- Repeat customers = 77

Result:

    81.91%

This is a period-level repeat purchase metric.

It is not a retention rate, cohort retention metric, or lifetime retention metric.

---

## 8.4 Customer Value

### Definition

Customer Value represents average completed revenue generated per purchasing customer during the selected observation period.

### Formula

    Customer Value =
    Completed Revenue / Purchasing Customers

The Week 4 validated full-dataset result is:

    AED 4,587.00

This metric is period-based and should not be interpreted as Customer Lifetime Value (CLV).

---

## 8.5 Payment Success Rate

### Definition

Payment Success Rate is the percentage of all recorded transactions whose status is `completed`.

### Formula

    Payment Success Rate =
    Completed Transactions / Total Transactions × 100

For the full dataset:

- Total transactions = 500
- Completed transactions = 288

Result:

    57.60%

---

# 9. Analytical Visualizations

The dashboard contains five primary analytical visualizations.

## 9.1 Monthly Revenue Trend

A line chart displays completed transaction revenue by month.

### Purpose

The visualization is designed to:

- Show revenue movement over time
- Identify month-to-month fluctuations
- Provide temporal context for business performance
- Allow the effect of date filters to be observed

The chart uses completed transaction revenue so that its definition is consistent with the formal revenue KPI.

The dataset shows substantial month-to-month variation.

The visualization is not used to claim a long-term trend or recurring annual seasonality.

---

## 9.2 Revenue by Product Category

A horizontal bar chart displays revenue attributed to product categories.

Order-item revenue is calculated using:

    Revenue = Quantity × Unit Price

The validated full-dataset category results are:

- Computer Accessories: AED 292,562.02
- Office: AED 213,568.44
- Electronics: AED 140,710.93
- Mobile Accessories: AED 115,302.41

Horizontal bars were selected because category names are relatively long and are easier to read on a horizontal axis.

The chart uses line-item revenue and therefore has a different analytical definition from transaction-level completed revenue.

---

## 9.3 Order Status Distribution

A bar chart displays the number of orders for each order status.

The available order statuses include:

- `pending`
- `confirmed`
- `shipped`
- `delivered`
- `cancelled`

The visualization is intended to show the distribution of current order statuses.

It is not interpreted as a conversion funnel because the dataset does not contain complete order-status transition histories.

---

## 9.4 Customer Activity Distribution

A histogram displays the distribution of recorded events per customer.

The metric is:

    Recorded Events per Customer

The histogram is intended to show how event records are distributed across customers.

It should not be interpreted as a formal customer engagement score.

The event data represents observed recorded activities rather than a validated engagement model.

A median reference line is included to provide a central tendency reference.

---

## 9.5 Transaction Amount Distribution

A histogram displays the distribution of transaction amounts.

The visualization is used to understand:

- Distribution shape
- Central tendency
- Spread
- Potential skewness
- Potential outliers

Mean and median reference lines are included.

The transaction amount distribution is right-skewed, with the mean above the median.

Two observations were identified as IQR-based statistical outliers during the EDA stage.

They were retained because there was no evidence that they represented invalid records.

---

# 10. Dashboard Layout

The dashboard is organized into the following sections:

    Dashboard Title
          |
          v
    Active Filter Information
          |
          v
    KPI Cards
          |
          v
    Filtered Data Overview
          |
          v
    Monthly Revenue Trend
          |
          v
    Revenue by Product Category
          |
          v
    Order Status Distribution
          |
          v
    Customer Activity Distribution
          |
          v
    Transaction Amount Distribution
          |
          v
    Dashboard Status

The layout is designed to place high-level business metrics before detailed analytical visualizations.

---

# 11. Visualization Design Principles

The Week 4 visualization design follows several principles.

## Chart intent

Each chart has a specific analytical purpose.

- Line chart → temporal revenue movement
- Horizontal bar chart → category comparison
- Bar chart → order status counts
- Histogram → customer activity distribution
- Histogram → transaction amount distribution

## Labels

Charts include descriptive titles and axis labels so that users can understand the metric without relying entirely on surrounding text.

## Scales

The chart types were selected based on the nature of the underlying variables.

## Annotation

Important values such as category revenue and central tendency measures are annotated where useful.

## Readability

Horizontal bars are used for category names because they improve readability compared with vertically rotated category labels.

---

# 12. Empty-State Handling

The dashboard explicitly handles empty filtered datasets.

When filters produce no available data, the relevant dashboard section displays an informational message instead of raising an exception.

Examples include:

    No revenue data is available for the selected filters.

    No order status data is available for the selected filters.

    No customer activity data is available for the selected filters.

This behavior was manually tested.

Clearing all product categories resulted in zero dependent metrics and appropriate empty-state messages without causing the dashboard to crash.

---

# 13. Validation Performed

The dashboard was tested using several filter scenarios.

## 13.1 Date Filter Test

A restricted date range was selected:

    2025-07-08 → 2025-08-08

The dashboard responded by changing:

- Transaction count
- Completed revenue
- AOV
- Repeat purchase rate
- Customer value
- Payment success rate
- Customer activity
- Other dependent visualizations

Observed result:

- 25 transactions
- 67 order items
- 21 customers represented
- Completed revenue: AED 21,825.74
- AOV: AED 1,678.90
- Repeat Purchase Rate: 8.33%
- Customer Value: AED 1,818.81
- Payment Success Rate: 52.00%

Status:

    PASS

---

## 13.2 Country Filter Test

A single country was selected.

The dashboard correctly changed:

- Customer population
- Transactions
- KPIs
- Charts

Status:

    PASS

---

## 13.3 Product Category Filter Test

The `Electronics` category was selected.

The dashboard correctly updated the dependent analytical population.

Status:

    PASS

---

## 13.4 Empty Category Test

All product categories were cleared.

The dependent metrics reduced to zero and relevant charts displayed informational empty-state messages.

The dashboard remained functional.

Status:

    PASS

---

# 14. KPI Validation

The dashboard KPI calculations were validated against the reusable KPI implementation and SQL calculations.

The following values matched between Python and SQL:

- Total transactions = 500
- Completed transactions = 288
- Payment Success Rate = 57.60%
- Completed Revenue = AED 431,177.98
- Completed Orders = 288
- AOV = AED 1,497.15
- Purchasing Customers = 94
- Repeat Customers = 77
- Repeat Purchase Rate = 81.91%
- Customer Value = AED 4,587.00

Monthly completed revenue and monthly revenue growth calculations also matched between Python and SQL.

This validation reduces the risk of presenting inconsistent KPI definitions across the analytics layer.

---

# 15. Important Analytical Assumptions

## Revenue Definition

Formal dashboard revenue uses completed transactions only.

Failed transactions are excluded.

Refunded transactions are excluded from completed revenue because the KPI is intended to represent successfully completed transactions.

The transaction dataset does not contain a separate refund amount field.

Therefore, a precise net-revenue-after-refunds calculation is not performed.

---

## Category-Filtered Revenue

When a product category is selected, the dashboard identifies orders containing products from the selected category.

Transaction-level KPI values therefore represent completed transactions associated with the filtered orders.

They should not be interpreted as category-attributed transaction revenue when an order contains multiple product categories.

The category revenue visualization itself calculates line-item revenue using:

    Quantity × Unit Price

for the selected order items.

---

## Repeat Purchase Rate

Repeat Purchase Rate is calculated over the selected observation period.

A customer is classified as a repeat purchaser when they have at least two unique completed orders during that period.

It is not a 30-day, 90-day, cohort-based, or lifetime retention metric.

---

## Customer Value

Customer Value is calculated as completed revenue divided by purchasing customers during the selected period.

It is not Customer Lifetime Value.

---

## Customer Activity

Customer activity represents recorded event counts.

It is not a formally validated customer engagement score.

---

## Order Status

Order status distribution represents the current order-status values present in the dataset.

Because status transitions are not stored, the visualization should not be interpreted as a conversion funnel.

---

## Synthetic Dataset Context

The underlying project dataset is synthetic.

Therefore, dashboard observations demonstrate the analytics workflow, KPI engineering, validation process, and dashboard implementation rather than representing actual e-commerce business performance.

---

# 16. Performance Considerations

The dashboard uses Streamlit data caching through `st.cache_data`.

This reduces repeated disk reads when users interact with filters.

The dashboard works with the curated datasets generated by the Week 3 pipeline rather than repeatedly processing raw source files.

This keeps the analytics layer separated from raw ingestion and reduces unnecessary processing during dashboard interaction.

---

# 17. Dashboard Implementation

The main dashboard implementation is:

    05_analytics/analytics_dashboard.py

The reusable KPI calculation module is:

    05_analytics/kpis.py

The exploratory analysis notebook is:

    05_analytics/eda.ipynb

The dashboard therefore separates:

- Exploratory analysis
- KPI calculation
- Interactive visualization

This makes the Week 4 analytics layer easier to validate and maintain.

---

# 18. Week 4 Outcome

The dashboard fulfills the Week 4 dashboard requirement by providing:

- Interactive date filtering
- Country filtering
- Product-category filtering
- Cached curated-data access
- Business KPI cards
- Revenue analysis
- Customer activity analysis
- Order-status analysis
- Transaction-value analysis
- Empty-state handling
- KPI validation
- Business-oriented analytical exploration

The dashboard is connected directly to the curated output of the Week 3 data engineering pipeline rather than the raw source data.

The resulting analytics layer provides a foundation for the machine-learning, retrieval, and agent components planned for later weeks.