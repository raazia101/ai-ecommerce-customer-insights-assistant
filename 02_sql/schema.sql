-- ============================================================
-- Week 2 - Day 3
-- Raw-to-Mart Warehouse Schema
-- ============================================================
--
-- Architecture:
--     RAW -> STAGING -> MART
--
-- Mart follows a star-schema design:
--     dim_customer
--     dim_product
--     dim_order
--     dim_date
--             |
--             v
--     fact_order_items
--
-- Fact grain:
--     One row represents one product line within one order.
--
-- ============================================================


-- ============================================================
-- 1. SCHEMAS
-- ============================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;


-- ============================================================
-- 2. RAW LAYER
-- ============================================================
-- Raw tables preserve source data with minimal transformation.
-- These tables mirror the public source tables used in Week 1.
--
-- In the current implementation, raw tables were populated
-- using CREATE TABLE AS SELECT from public.*.
-- ============================================================


-- ============================================================
-- 3. STAGING LAYER
-- ============================================================
-- Staging applies lightweight transformations such as:
--   - trimming text
--   - standardizing case
--   - deriving item_revenue
--
-- Current staging tables:
--   staging.customers
--   staging.products
--   staging.orders
--   staging.order_items
-- ============================================================


-- ============================================================
-- 4. MART DIMENSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS mart.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,

    -- SCD Type 2 fields
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE IF NOT EXISTS mart.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL
    CONSTRAINT uq_dim_product_business_key UNIQUE (product_id)
);


CREATE TABLE IF NOT EXISTS mart.dim_order (
    order_key BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL,
    currency VARCHAR(10) NOT NULL
    CONSTRAINT uq_dim_order_business_key UNIQUE (order_id)
);


CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL
);


-- ============================================================
-- 5. FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS mart.fact_order_items (
    order_item_key BIGSERIAL PRIMARY KEY,

    order_key BIGINT NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    date_key INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    item_revenue NUMERIC(12,2) NOT NULL,

    -- Dimension relationships
    CONSTRAINT fk_fact_order
        FOREIGN KEY (order_key)
        REFERENCES mart.dim_order(order_key),

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES mart.dim_customer(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES mart.dim_product(product_key),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES mart.dim_date(date_key),

    -- Data-quality constraints
    CONSTRAINT chk_fact_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_fact_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_fact_revenue
        CHECK (item_revenue >= 0)
);


-- ============================================================
-- 6. DESIGN NOTES
-- ============================================================
--
-- Natural/business keys:
--   customer_id
--   product_id
--   order_id
--   order_item_id
--
-- Surrogate keys:
--   customer_key
--   product_key
--   order_key
--   order_item_key
--
-- SCD Type 2:
--   dim_customer stores valid_from, valid_to and is_current
--   so historical versions of a customer can be preserved.
--
-- Fact table:
--   fact_order_items stores measurable business events:
--   quantity, unit_price and item_revenue.
--
-- Date dimension:
--   dim_date provides reusable calendar attributes for
--   time-based analytics.
--
-- ============================================================