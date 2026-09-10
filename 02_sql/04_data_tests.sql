-- Week 2 Day 5: Data Quality Tests
-- Purpose: Validate warehouse completeness, integrity, and validity.


-- Test 1: Staging-to-fact row count consistency
SELECT
    (SELECT COUNT(*) FROM staging.order_items) AS staging_rows,
    (SELECT COUNT(*) FROM mart.fact_order_items) AS fact_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.order_items)
           = (SELECT COUNT(*) FROM mart.fact_order_items)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS test_result;


-- Test 2: Fact-table foreign-key integrity
SELECT
    COUNT(*) AS orphaned_rows,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS test_result
FROM mart.fact_order_items f
LEFT JOIN mart.dim_customer c
    ON f.customer_key = c.customer_key
LEFT JOIN mart.dim_product p
    ON f.product_key = p.product_key
LEFT JOIN mart.dim_order o
    ON f.order_key = o.order_key
LEFT JOIN mart.dim_date d
    ON f.date_key = d.date_key
WHERE c.customer_key IS NULL
   OR p.product_key IS NULL
   OR o.order_key IS NULL
   OR d.date_key IS NULL;


-- Test 3: NULL and invalid-value checks
SELECT
    COUNT(*) FILTER (WHERE order_key IS NULL) AS null_order_keys,
    COUNT(*) FILTER (WHERE customer_key IS NULL) AS null_customer_keys,
    COUNT(*) FILTER (WHERE product_key IS NULL) AS null_product_keys,
    COUNT(*) FILTER (WHERE date_key IS NULL) AS null_date_keys,
    COUNT(*) FILTER (WHERE quantity <= 0) AS invalid_quantities,
    COUNT(*) FILTER (WHERE unit_price < 0) AS invalid_prices,
    COUNT(*) FILTER (WHERE item_revenue < 0) AS invalid_revenue
FROM mart.fact_order_items;