# Data Dictionary

Synthetic Pakistani e-commerce marketplace data. Not real company data.

## raw.customers

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| customer_id | INTEGER | Unique customer identifier | 10023 | No | customers | Primary business key |
| first_name | VARCHAR | Given name (synthetic) | Ahmed | No | customers | Customer first name |
| last_name | VARCHAR | Family name (synthetic) | Khan | No | customers | Customer last name |
| email | VARCHAR | Synthetic email | ahmed.khan1@example.pk | No | customers | Contact email |
| phone | VARCHAR | PK-format mobile | +92-300-1234567 | Yes | customers | Contact phone |
| gender | VARCHAR | Gender category | Male | Yes | customers | Demographic attribute |
| birth_date | DATE | Date of birth | 1992-05-14 | Yes | customers | Demographic attribute |
| location_id | INTEGER | FK to locations | 2 | No | customers | Home city reference |
| registration_date | DATE | Account created | 2021-03-01 | No | customers | Tenure start |
| is_active | BOOLEAN | Account active flag | true | No | customers | Eligibility flag |
| loaded_at | TIMESTAMPTZ | ETL load timestamp | 2026-01-01T00:00:00Z | No | ETL | Audit |
| source_file | TEXT | Source filename | customers.csv | Yes | ETL | Lineage |

## raw.products

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| product_id | INTEGER | Unique product id | 501 | No | products | Primary key |
| product_name | VARCHAR | Product title | PakTech Phone X12 | No | products | Sellable item name |
| category_id | INTEGER | FK to categories | 2 | No | products | Merchandising category |
| seller_id | INTEGER | FK to sellers | 88 | No | products | Offering seller |
| brand | VARCHAR | Brand label | PakTech | Yes | products | Brand attribute |
| unit_price | NUMERIC | List price PKR | 89999.00 | No | products | Selling price |
| cost_price | NUMERIC | Cost PKR | 65000.00 | No | products | COGS proxy |
| weight_kg | NUMERIC | Weight | 0.180 | Yes | products | Logistics attribute |
| is_active | BOOLEAN | Listed flag | true | No | products | Availability |

## raw.orders

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| order_id | BIGINT | Unique order id | 100234 | No | orders | Primary business identifier |
| customer_id | INTEGER | FK to customers | 10023 | No | orders | Purchaser |
| order_date | TIMESTAMP | Order placed at | 2024-06-01 14:22:00 | No | orders | Order event time |
| order_status | VARCHAR | Lifecycle status | Delivered | No | orders | Fulfillment state |
| location_id | INTEGER | Ship-to location | 1 | No | orders | Delivery geography |
| shipping_fee | NUMERIC | Shipping PKR | 200.00 | No | orders | Logistics fee |
| discount_amount | NUMERIC | Order discount PKR | 500.00 | No | orders | Promotion value |
| total_amount | NUMERIC | Order total PKR | 15400.00 | No | orders | Amount charged |
| currency | VARCHAR | Currency code | PKR | No | orders | Currency |

## raw.order_items

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| order_item_id | BIGINT | Unique line id | 900001 | No | order_items | Line grain key |
| order_id | BIGINT | FK to orders | 100234 | No | order_items | Parent order |
| product_id | INTEGER | FK to products | 501 | No | order_items | Purchased product |
| seller_id | INTEGER | FK to sellers | 88 | No | order_items | Fulfilling seller |
| quantity | INTEGER | Units purchased | 2 | No | order_items | Units |
| unit_price | NUMERIC | Price at purchase | 89999.00 | No | order_items | Price snapshot |
| discount_amount | NUMERIC | Line discount | 1000.00 | No | order_items | Line promotion |
| line_total | NUMERIC | Net line amount | 178998.00 | No | order_items | Extended amount |

## raw.payments

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| payment_id | BIGINT | Payment id | 100234 | No | payments | Payment key |
| order_id | BIGINT | FK to orders | 100234 | No | payments | Paid order |
| payment_method | VARCHAR | Method | Cash on Delivery | No | payments | Tender type |
| payment_status | VARCHAR | Status | Paid | No | payments | Settlement state |
| payment_amount | NUMERIC | Amount PKR | 15400.00 | No | payments | Tender amount |
| payment_date | TIMESTAMP | Payment time | 2024-06-03 18:00:00 | No | payments | Settlement time |
| transaction_ref | VARCHAR | Reference | TXN-100234 | Yes | payments | External ref |

## raw.shipments

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| shipment_id | BIGINT | Shipment id | 100234 | No | shipments | Shipment key |
| order_id | BIGINT | FK to orders | 100234 | No | shipments | Shipped order |
| carrier | VARCHAR | Courier | TCS | No | shipments | Logistics partner |
| shipment_date | TIMESTAMP | Shipped at | 2024-06-02 | Yes | shipments | Dispatch time |
| delivery_date | TIMESTAMP | Delivered at | 2024-06-05 | Yes | shipments | Delivery time |
| promised_delivery_date | DATE | Promise date | 2024-06-06 | Yes | shipments | SLA date |
| delivery_status | VARCHAR | Status | Delivered | No | shipments | Logistics state |
| tracking_number | VARCHAR | Tracking | PK100234 | Yes | shipments | Tracking id |

## raw.returns

| Column | Data Type | Description | Example | Nullable | Source | Business Meaning |
|--------|-----------|-------------|---------|----------|--------|------------------|
| return_id | BIGINT | Return id | 30001 | No | returns | Return key |
| order_id | BIGINT | FK to orders | 100234 | No | returns | Parent order |
| order_item_id | BIGINT | FK to order_items | 900001 | No | returns | Returned line |
| return_date | TIMESTAMP | Return created | 2024-06-10 | No | returns | Return event |
| return_reason | VARCHAR | Reason code | Damaged | No | returns | Why returned |
| refund_amount | NUMERIC | Refund PKR | 89999.00 | No | returns | Money returned |
| return_status | VARCHAR | Status | Completed | No | returns | Return workflow |

## analytics facts (summary)

See `docs/warehouse_design.md` for grains. Surrogate keys (`*_key`) mirror natural keys in this project for BI simplicity; in larger systems they would be warehouse-generated sequences.
