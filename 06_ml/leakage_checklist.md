# Week 5 — ML Data Leakage Checklist

## Purpose

This checklist ensures that the machine learning dataset does not use information that would have been unavailable at the time the prediction was made.

## Prediction Cutoff

`2026-05-24 00:00:00`

## Feature Data Rule

All model features must be based only on information satisfying:

`timestamp/date <= 2026-05-24 00:00:00`

## Target Data Rule

The target must be calculated only from future behaviour satisfying:

`2026-05-24 00:00:00 < timestamp/date <= 2026-08-22 00:00:00`

## Customer Eligibility

Only customers satisfying:

`signup_date <= 2026-05-24 00:00:00`

may be included.

## Transaction Leakage Checks

Do not use:

- future completed transactions
- future transaction revenue
- future transaction counts
- future transaction statuses
- future order activity

as input features.

## Event Leakage Checks

Do not use events occurring after the prediction cutoff.

Future:

- product views
- add-to-cart events
- checkout events
- searches
- logins
- purchases
- other customer interactions

must not be included in feature calculations.

## Aggregation Leakage

Customer-level aggregates must be calculated after filtering the source data to the historical period.

For example, lifetime revenue must mean revenue accumulated up to the prediction cutoff, not revenue across the entire dataset.

## Target Leakage

Do not use any feature that directly or indirectly reveals whether the customer purchased during the future prediction window.

Examples of prohibited features:

- future_purchase_count
- future_revenue
- future_completed_transaction_count
- future_order_count
- future_product_views

## Join Leakage

When joining:

`transactions → orders → order_items → products`

only historical records may contribute to features.

The existence of a future order or transaction must not cause a customer to receive information about that future behaviour.

## Evaluation Leakage

The target must not be used during feature engineering.

The test/evaluation data must not be used to tune the model before final evaluation.

## Final Verification

Before model training, verify:

- [ ] All customers were eligible at the cutoff.
- [ ] All transaction features use dates <= cutoff.
- [ ] All event features use timestamps <= cutoff.
- [ ] No future transaction information appears in features.
- [ ] No future event information appears in features.
- [ ] The target uses only the future prediction window.
- [ ] No target-derived feature exists.
- [ ] Aggregations were performed after applying the temporal cutoff.
- [ ] Train/test splitting is performed appropriately for the small dataset.