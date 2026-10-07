-- Raw layer DDL for Pakistan E-commerce Analytics Platform
-- Idempotent: safe to re-run.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS ops;

-- ---------------------------------------------------------------------------
-- Ops: pipeline monitoring
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
    pipeline_run_id     BIGSERIAL PRIMARY KEY,
    pipeline_name       VARCHAR(100) NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time            TIMESTAMPTZ,
    status              VARCHAR(30) NOT NULL DEFAULT 'running',
    rows_processed      BIGINT DEFAULT 0,
    rows_failed         BIGINT DEFAULT 0,
    error_message       TEXT,
    metadata            JSONB
);

CREATE TABLE IF NOT EXISTS ops.data_freshness (
    table_name          VARCHAR(100) PRIMARY KEY,
    last_successful_load TIMESTAMPTZ NOT NULL,
    row_count           BIGINT,
    source_file         TEXT,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Locations
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS raw.returns CASCADE;
DROP TABLE IF EXISTS raw.shipments CASCADE;
DROP TABLE IF EXISTS raw.payments CASCADE;
DROP TABLE IF EXISTS raw.order_items CASCADE;
DROP TABLE IF EXISTS raw.orders CASCADE;
DROP TABLE IF EXISTS raw.products CASCADE;
DROP TABLE IF EXISTS raw.customers CASCADE;
DROP TABLE IF EXISTS raw.sellers CASCADE;
DROP TABLE IF EXISTS raw.categories CASCADE;
DROP TABLE IF EXISTS raw.locations CASCADE;

CREATE TABLE raw.locations (
    location_id     INTEGER PRIMARY KEY,
    city            VARCHAR(100) NOT NULL,
    province        VARCHAR(100) NOT NULL,
    region          VARCHAR(50) NOT NULL,
    country         VARCHAR(50) NOT NULL DEFAULT 'Pakistan',
    latitude        NUMERIC(9, 6),
    longitude       NUMERIC(9, 6),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file     TEXT
);

CREATE TABLE raw.categories (
    category_id     INTEGER PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL UNIQUE,
    parent_category VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file     TEXT
);

CREATE TABLE raw.sellers (
    seller_id           INTEGER PRIMARY KEY,
    seller_name         VARCHAR(200) NOT NULL,
    business_type       VARCHAR(50) NOT NULL,
    location_id         INTEGER NOT NULL REFERENCES raw.locations(location_id),
    registration_date   DATE NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    rating              NUMERIC(3, 2),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.customers (
    customer_id         INTEGER PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL,
    phone               VARCHAR(20),
    gender              VARCHAR(20),
    birth_date          DATE,
    location_id         INTEGER NOT NULL REFERENCES raw.locations(location_id),
    registration_date   DATE NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.products (
    product_id          INTEGER PRIMARY KEY,
    product_name        VARCHAR(255) NOT NULL,
    category_id         INTEGER NOT NULL REFERENCES raw.categories(category_id),
    seller_id           INTEGER NOT NULL REFERENCES raw.sellers(seller_id),
    brand               VARCHAR(100),
    unit_price          NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    cost_price          NUMERIC(12, 2) NOT NULL CHECK (cost_price >= 0),
    weight_kg           NUMERIC(8, 3),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.orders (
    order_id            BIGINT PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES raw.customers(customer_id),
    order_date          TIMESTAMP NOT NULL,
    order_status        VARCHAR(30) NOT NULL,
    location_id         INTEGER NOT NULL REFERENCES raw.locations(location_id),
    shipping_fee        NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0),
    discount_amount     NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount        NUMERIC(14, 2) NOT NULL CHECK (total_amount >= 0),
    currency            VARCHAR(3) NOT NULL DEFAULT 'PKR',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.order_items (
    order_item_id       BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL REFERENCES raw.orders(order_id),
    product_id          INTEGER NOT NULL REFERENCES raw.products(product_id),
    seller_id           INTEGER NOT NULL REFERENCES raw.sellers(seller_id),
    quantity            INTEGER NOT NULL CHECK (quantity > 0),
    unit_price          NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount_amount     NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    line_total          NUMERIC(14, 2) NOT NULL CHECK (line_total >= 0),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.payments (
    payment_id          BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL REFERENCES raw.orders(order_id),
    payment_method      VARCHAR(50) NOT NULL,
    payment_status      VARCHAR(30) NOT NULL,
    payment_amount      NUMERIC(14, 2) NOT NULL CHECK (payment_amount >= 0),
    payment_date        TIMESTAMP NOT NULL,
    transaction_ref     VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

CREATE TABLE raw.shipments (
    shipment_id         BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL REFERENCES raw.orders(order_id),
    carrier             VARCHAR(100) NOT NULL,
    shipment_date       TIMESTAMP,
    delivery_date       TIMESTAMP,
    promised_delivery_date DATE,
    delivery_status     VARCHAR(50) NOT NULL,
    tracking_number     VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT,
    CONSTRAINT chk_delivery_after_shipment
        CHECK (delivery_date IS NULL OR shipment_date IS NULL OR delivery_date >= shipment_date)
);

CREATE TABLE raw.returns (
    return_id           BIGINT PRIMARY KEY,
    order_id            BIGINT NOT NULL REFERENCES raw.orders(order_id),
    order_item_id       BIGINT NOT NULL REFERENCES raw.order_items(order_item_id),
    return_date         TIMESTAMP NOT NULL,
    return_reason       VARCHAR(100) NOT NULL,
    refund_amount       NUMERIC(14, 2) NOT NULL CHECK (refund_amount >= 0),
    return_status       VARCHAR(50) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file         TEXT
);

-- Indexes for analytical load performance
CREATE INDEX idx_raw_customers_location ON raw.customers(location_id);
CREATE INDEX idx_raw_products_category ON raw.products(category_id);
CREATE INDEX idx_raw_products_seller ON raw.products(seller_id);
CREATE INDEX idx_raw_orders_customer ON raw.orders(customer_id);
CREATE INDEX idx_raw_orders_date ON raw.orders(order_date);
CREATE INDEX idx_raw_orders_status ON raw.orders(order_status);
CREATE INDEX idx_raw_order_items_order ON raw.order_items(order_id);
CREATE INDEX idx_raw_order_items_product ON raw.order_items(product_id);
CREATE INDEX idx_raw_payments_order ON raw.payments(order_id);
CREATE INDEX idx_raw_payments_method ON raw.payments(payment_method);
CREATE INDEX idx_raw_shipments_order ON raw.shipments(order_id);
CREATE INDEX idx_raw_returns_order ON raw.returns(order_id);
CREATE INDEX idx_raw_returns_item ON raw.returns(order_item_id);
