# E-commerce Customer Insights Assistant
# Week 4 Analytics Report

## 1. Executive Summary

Week 4 focused on transforming the curated data produced by the Week 3 data engineering pipeline into defensible business insights and an interactive analytics dashboard.

The work covered:

- Exploratory Data Analysis (EDA)
- Data-quality investigation
- Analytical visualization
- Business KPI engineering
- Python-to-SQL KPI validation
- Interactive Streamlit dashboard development
- Dashboard testing
- Business insight storytelling

The resulting analytics layer provides an interactive interface for examining transaction performance, customer purchasing behavior, customer activity, product-category revenue, order statuses, and transaction-value distributions.

The underlying project dataset is synthetic, so the results demonstrate the analytics workflow and engineering implementation rather than actual business performance.

---

# 2. Objectives

The objectives of Week 4 were to:

1. Profile the curated datasets.
2. Identify missing values, duplicates, outliers, and unusual distributions.
3. Analyze relationships and trends in the available data.
4. Create publication-quality analytical visualizations.
5. Engineer business KPIs with explicit definitions.
6. Validate KPI calculations against SQL.
7. Build an interactive Streamlit dashboard.
8. Test dashboard filtering and empty-state behavior.
9. Develop a concise business insight narrative.
10. Document assumptions and analytical limitations.

---

# 3. Data Used

The analytics layer uses the curated datasets produced by the Week 3 pipeline.

The datasets are:

- `customers.parquet`
- `products.parquet`
- `orders.parquet`
- `order_items.parquet`
- `transactions.parquet`
- `events.parquet`

The datasets are stored under:

    data/curated/

The dashboard and analytics work do not directly consume the original raw CSV and JSON files.

---

# 4. Dataset Size

The curated datasets used for Week 4 contain:

| Dataset | Rows |
|---|---:|
| Customers | 7,482 |
| Products | 5,456 |
| Orders | 11,817 |
| Order Items | 19,506 |
| Transactions | 19,823 |
| Events | 22,760 |

The corresponding business-level source entities represented in the synthetic dataset include:

- 100 customers
- 50 products
- 500 orders
- 1,488 order items
- 500 transactions
- 1,000 events

The larger curated row counts are the result of the Week 3 pipeline's historical/incremental curated outputs.

---

# 5. Exploratory Data Analysis

Exploratory analysis was performed in:

    05_analytics/eda.ipynb

The EDA focused on:

- Dataset structure
- Missingness
- Duplicate records
- Key uniqueness
- Numerical distributions
- Outlier detection
- Correlations
- Temporal behavior
- Event-type distribution

The analysis was designed to distinguish direct observations from interpretations.

---

# 6. Data Quality Findings

## 6.1 Duplicate Records

No duplicate records were identified in the analyzed datasets.

The key uniqueness checks also passed for the relevant business entities.

---

## 6.2 Event Missingness

The events dataset contains expected structural missingness.

The missing fields depend on the type of event.

For example:

- Login and logout events do not require a product or order.
- Search events do not require a product or order.
- Product-view events contain product information but not an order.
- Purchase events contain order information but not necessarily product information.

Therefore, missing `product_id` or `order_id` values in the event dataset cannot automatically be classified as data-quality errors.

This is an example of why missingness must be interpreted according to the meaning of the record rather than treated as a simple null-count problem.

---

# 7. Outlier Analysis

The transaction amount distribution was analyzed using the Interquartile Range (IQR) method.

The transaction amount statistics were:

| Statistic | Amount (AED) |
|---|---:|
| Mean | 1,524.29 |
| Standard Deviation | 945.28 |
| Minimum | 21.14 |
| Q1 | 790.50 |
| Median | 1,399.39 |
| Q3 | 2,167.55 |
| Maximum | 4,351.92 |

The IQR-based upper threshold was:

    AED 4,233.12

Two transaction amounts were above this threshold.

They were:

| Transaction | Order | Customer | Amount |
|---|---|---|---:|
| TXN-00127 | ORD-00127 | CUST-0068 | AED 4,252.73 |
| TXN-00318 | ORD-00318 | CUST-0040 | AED 4,351.92 |

These observations were retained.

The IQR method identifies statistical outliers, but being an outlier does not automatically mean that a record is incorrect.

No evidence was found in the available data that these transactions represented invalid records.

---

# 8. Correlation Analysis

Two numerical relationships were examined.

## Product Price vs Stock Quantity

Correlation:

    0.106151

This represents a weak linear association.

## Order Item Quantity vs Unit Price

Correlation:

    0.005556

This also represents a very weak linear association.

The correlations should not be interpreted as proof that no relationship exists.

They only describe the strength of linear association in the available variables.

---

# 9. Temporal Analysis

Monthly transaction activity was examined across the available observation period.

The monthly transaction series does not show a clear sustained monotonic increase or decrease.

There is substantial month-to-month variation.

The available synthetic data covers approximately 20 months, which is insufficient to confidently establish a recurring annual seasonal pattern.

Therefore, the analysis avoids labeling the observed fluctuations as confirmed seasonality.

---

# 10. Event Distribution

The event types were relatively distributed across the available event records.

Observed counts included:

| Event Type | Count |
|---|---:|
| product_view | 129 |
| login | 122 |
| purchase | 115 |
| search | 113 |
| add_to_cart | 112 |
| page_view | 109 |
| checkout_started | 102 |
| remove_from_cart | 101 |
| logout | 97 |

These are raw event counts.

They should not be interpreted as conversion rates because the data does not establish a complete user-level conversion funnel from these counts alone.

---

# 11. Visual Analytics

Five main visualizations were developed for the dashboard.

## 11.1 Monthly Revenue Trend

A line chart shows completed transaction revenue by month.

The chart is based on the formal revenue definition used by the KPI layer:

    Completed Revenue =
    Sum of transaction amount where status = completed

The chart is used to identify month-to-month revenue fluctuations.

---

## 11.2 Revenue by Product Category

Revenue was calculated at the order-item level:

    Revenue = Quantity × Unit Price

The full-dataset category results were:

| Category | Revenue (AED) |
|---|---:|
| Computer Accessories | 292,562.02 |
| Office | 213,568.44 |
| Electronics | 140,710.93 |
| Mobile Accessories | 115,302.41 |

Computer Accessories has the highest line-item revenue in the analyzed dataset.

This result should be understood as category-level order-item revenue rather than transaction-level completed revenue.

---

## 11.3 Order Status Distribution

The dashboard displays the distribution of order statuses.

The available statuses include:

- pending
- confirmed
- shipped
- delivered
- cancelled

The visualization is descriptive.

It is not treated as a conversion funnel because complete status-transition history is not available.

---

## 11.4 Customer Activity Distribution

Customer activity was represented as recorded event counts per customer.

The resulting histogram shows how recorded events are distributed across customers.

This metric is not treated as a formal engagement score because the available data does not provide a validated engagement model.

---

## 11.5 Transaction Amount Distribution

The transaction amount histogram shows the distribution and skewness of transaction values.

The mean and median were included as reference points.

The mean was above the median, consistent with the presence of higher-value transactions and right-skewed distribution.

---

# 12. KPI Engineering

Five business KPIs were engineered.

---

## 12.1 Completed Revenue

Definition:

> Sum of transaction amounts for transactions with status `completed`.

Formula:

    Completed Revenue =
    SUM(amount where status = completed)

Result:

    AED 431,177.98

---

## 12.2 Average Order Value

Definition:

> Completed revenue divided by the number of unique completed orders.

Formula:

    AOV =
    Completed Revenue / Unique Completed Orders

Result:

    AED 1,497.15

There were 288 completed transactions/orders in the validated full dataset.

---

## 12.3 Payment Success Rate

Definition:

> Percentage of all transactions whose status is `completed`.

Formula:

    Payment Success Rate =
    Completed Transactions / Total Transactions × 100

Values:

- Total transactions = 500
- Completed transactions = 288

Result:

    57.60%

---

## 12.4 Repeat Purchase Rate

Definition:

> Percentage of purchasing customers who completed at least two unique orders during the selected observation period.

Values:

- Purchasing customers = 94
- Repeat customers = 77

Formula:

    Repeat Purchase Rate =
    Repeat Customers / Purchasing Customers × 100

Result:

    81.91%

This is a period-level repeat-purchase metric.

It is not equivalent to cohort retention, monthly retention, or lifetime retention.

---

## 12.5 Customer Value

Definition:

> Completed revenue divided by the number of purchasing customers during the selected observation period.

Formula:

    Customer Value =
    Completed Revenue / Purchasing Customers

Result:

    AED 4,587.00

This is a period-based customer value metric.

It is not Customer Lifetime Value (CLV).

---

# 13. KPI Validation

The KPI calculations implemented in Python were independently compared against SQL calculations.

The results matched.

| KPI / Check | Result |
|---|---:|
| Total transactions | 500 |
| Completed transactions | 288 |
| Payment Success Rate | 57.60% |
| Completed Revenue | AED 431,177.98 |
| Completed Orders | 288 |
| AOV | AED 1,497.15 |
| Purchasing Customers | 94 |
| Repeat Customers | 77 |
| Repeat Purchase Rate | 81.91% |
| Customer Value | AED 4,587.00 |

Monthly completed revenue and monthly revenue-growth calculations also matched between Python and SQL.

This validation provides evidence that the KPI logic is consistent between the analytics implementation and the SQL warehouse layer.

---

# 14. KPI Definition Sheet

The KPI definitions used during Week 4 are summarized below.

| KPI | Definition | Formula | Source | Owner |
|---|---|---|---|---|
| Completed Revenue | Revenue from completed transactions | SUM(completed transaction amount) | transactions | Analytics |
| AOV | Average completed revenue per unique completed order | Completed Revenue / Completed Orders | transactions | Analytics |
| Repeat Purchase Rate | Percentage of purchasing customers with at least two completed orders | Repeat Customers / Purchasing Customers × 100 | transactions | Analytics |
| Customer Value | Average completed revenue per purchasing customer | Completed Revenue / Purchasing Customers | transactions | Analytics |
| Payment Success Rate | Percentage of transactions completed successfully | Completed Transactions / Total Transactions × 100 | transactions | Analytics |

---

# 15. Interactive Dashboard

The interactive dashboard was implemented using Streamlit.

Main implementation:

    05_analytics/analytics_dashboard.py

Reusable KPI implementation:

    05_analytics/kpis.py

The dashboard consumes the curated Parquet datasets from:

    data/curated/

---

# 16. Dashboard Features

The dashboard provides:

- Date filtering
- Country filtering
- Product-category filtering
- KPI cards
- Monthly revenue trend
- Category revenue comparison
- Order status distribution
- Customer activity distribution
- Transaction amount distribution
- Filtered data overview
- Empty-state handling

The dashboard also uses Streamlit caching to reduce repeated data loading.

---

# 17. Dashboard Filter Logic

## Date

The date filter is applied to transaction dates and event timestamps.

This ensures that customer activity is also restricted to the selected time period.

---

## Country

Country filtering first identifies the relevant customer IDs.

Those customer IDs are then used to filter transactions and downstream analytical datasets.

---

## Product Category

Product-category filtering first identifies relevant product IDs.

Those products are linked to order items.

The corresponding order IDs are then used to identify relevant transactions.

This allows the dashboard to propagate a category selection into transaction-level metrics.

---

# 18. Dashboard Testing

The dashboard was manually tested using multiple filter combinations.

## Date Filter

Test period:

    2025-07-08 → 2025-08-08

Observed results:

- 25 transactions
- 67 order items
- 21 customers represented
- Completed revenue: AED 21,825.74
- AOV: AED 1,678.90
- Repeat Purchase Rate: 8.33%
- Customer Value: AED 1,818.81
- Payment Success Rate: 52.00%

The KPI values and customer activity changed correctly.

Status:

    PASS

---

## Country Filter

A single country was selected.

The dashboard updated the relevant customer population, transactions, KPIs, and charts.

Status:

    PASS

---

## Product Category Filter

The `Electronics` category was selected.

The dependent dashboard outputs updated correctly.

Status:

    PASS

---

## Empty-State Test

All product categories were cleared.

The dashboard:

- Reduced dependent metrics to zero.
- Displayed informational empty-state messages.
- Did not crash.

Status:

    PASS

---

# 19. Business Insight Narrative

The Week 4 dashboard can be presented using the following five-minute narrative.

## Context

The purpose of the dashboard is to convert curated e-commerce data into business-facing insights.

The analysis focuses on:

- Transaction performance
- Customer purchasing behavior
- Revenue behavior
- Product-category performance

---

## Insight 1: Transaction Outcomes

The dataset contains 500 transactions.

Of these:

- 288 were completed.
- 99 were failed.
- 113 were refunded.

The resulting Payment Success Rate is 57.60%.

This indicates that transaction outcomes are an important area for further analysis.

The available dataset alone does not establish why transactions failed or were refunded.

---

## Insight 2: Repeat Purchasing

There are 94 customers with completed purchases.

77 of these customers completed at least two unique orders during the observation period.

This produces a Repeat Purchase Rate of 81.91% under the Week 4 definition.

The result indicates substantial repeat purchasing within the observed synthetic dataset.

It should not be interpreted as a formal customer-retention rate.

---

## Insight 3: Revenue Fluctuation

Completed revenue varies substantially across months.

For example:

- February 2026: AED 9,567.01
- March 2026: AED 26,848.48
- July 2026: AED 33,105.04
- August 2026: AED 15,895.27

The available data therefore demonstrates significant month-to-month variation.

The analysis does not establish a recurring annual seasonal pattern.

---

## Insight 4: Category Revenue

Computer Accessories generated the highest line-item revenue:

    AED 292,562.02

The next category was Office:

    AED 213,568.44

This provides a starting point for examining product mix and category-level performance.

The figures are based on order-item revenue and should not automatically be treated as completed transaction revenue.

---

## Next Analytical Steps

Based on the observed patterns, useful follow-up analyses would include:

1. Investigating the causes of failed and refunded transactions.
2. Segmenting repeat purchasing by customer characteristics.
3. Examining repeat purchasing by product category.
4. Identifying products associated with consistently completed revenue.
5. Investigating customer behavior before completed purchases.
6. Building predictive models for repeat purchase or payment failure.

These are proposed analytical directions rather than conclusions about real business causes.

---

# 20. Limitations

Several limitations apply to the analysis.

## Synthetic Data

The dataset is synthetic.

Therefore, the results demonstrate the technical analytics workflow rather than actual commercial performance.

---

## Refund Information

The transaction dataset does not contain a separate refund amount.

Therefore, the analysis cannot calculate precise net revenue after refunds.

---

## Category Attribution

Category revenue is calculated at the order-item level.

When an order contains multiple product categories, transaction-level KPI filtering can associate the transaction with selected-category orders without providing an exact category-level allocation of the transaction amount.

---

## Repeat Purchase Definition

Repeat Purchase Rate is calculated over the selected observation period.

It is not a standardized retention or cohort metric.

---

## Customer Value

Customer Value is period-based.

It is not Customer Lifetime Value.

---

## Customer Activity

Recorded event count is not a validated customer engagement score.

---

## Seasonality

The available observation period is not sufficient to confidently establish recurring annual seasonality.

---

## Order Funnel

Order-status distribution is not a conversion funnel because historical status transitions are not available.

---

# 21. Technical Implementation

The main Week 4 files are:

    05_analytics/
    ├── eda.ipynb
    ├── kpis.py
    ├── analytics_dashboard.py
    ├── dashboard_design.md
    └── analytics_report.md

### `eda.ipynb`

Contains:

- Dataset profiling
- Missingness analysis
- Duplicate checks
- Outlier analysis
- Correlation analysis
- Temporal analysis
- Event distribution
- Data-quality observations

### `kpis.py`

Contains reusable KPI calculations for:

- Payment Success Rate
- Completed Revenue
- AOV
- Repeat Purchase Rate
- Customer Value

### `analytics_dashboard.py`

Contains:

- Streamlit dashboard
- Cached data loading
- Interactive filters
- KPI calculations
- Analytical charts
- Empty-state handling

### `dashboard_design.md`

Documents:

- Dashboard architecture
- Filter logic
- KPI definitions
- Visualization design
- Validation
- Analytical assumptions

---

# 22. Reproducibility

The Week 4 analytics layer depends on the curated outputs generated by the Week 3 data pipeline.

The expected data flow is:

    Raw Data
       |
       v
    Week 3 Pipeline
       |
       v
    Curated Parquet
       |
       v
    Week 4 Analytics
       |
       +----> EDA
       |
       +----> KPI Engine
       |
       +----> Dashboard

The dashboard can be launched with:

    streamlit run 05_analytics\analytics_dashboard.py

The Python KPI module can be executed independently to inspect the validated KPI outputs.

---

# 23. Week 4 Deliverables

The completed Week 4 analytics deliverables are:

- `05_analytics/eda.ipynb`
- `05_analytics/kpis.py`
- `05_analytics/analytics_dashboard.py`
- `05_analytics/dashboard_design.md`
- `05_analytics/analytics_report.md`

The work also includes:

- Five analytical visualizations
- Five validated business KPIs
- Python-to-SQL validation
- Interactive dashboard filters
- Empty-state testing
- Stakeholder-style dashboard demonstration
- Business insight narrative

---

# 24. Week 4 Acceptance Summary

The Week 4 implementation satisfies the analytics and dashboard objectives by providing:

- Exploratory analysis of curated data
- Data-quality observations
- Publication-quality visualizations
- Explicit KPI definitions
- KPI validation against SQL
- Interactive date filtering
- Country filtering
- Product-category filtering
- Cached data access
- KPI cards
- Drill-down analytical charts
- Empty-state handling
- Business insight narrative
- Documented analytical assumptions and limitations

The resulting analytics layer provides the business-facing foundation for the machine-learning and AI components that will be developed in subsequent project weeks.

---

# 25. Conclusion

Week 4 transformed the validated curated data produced during Week 3 into an interactive analytics product.

The work progressed from exploratory analysis to KPI engineering, visualization, validation, dashboard development, and stakeholder storytelling.

The most important engineering principle applied during the week was that business metrics should have explicit definitions and should be independently validated before being presented through a dashboard.

The resulting dashboard provides an interactive interface for exploring e-commerce performance while clearly documenting the assumptions and limitations associated with the synthetic dataset.

The Week 4 analytics layer therefore establishes a reliable foundation for the predictive and AI-driven capabilities planned for the later stages of the E-commerce Customer Insights Assistant.