# Business Metrics & KPI Definitions

All monetary values are in **PKR**. Definitions below are **project-specific** and documented for transparency.

## Revenue

| KPI | Business definition | SQL (conceptual) | DAX |
|-----|---------------------|------------------|-----|
| Gross Revenue | Sum of quantity × unit price before discounts/refunds | `sum(quantity * unit_price)` on order items | `SUM(fact_order_items[gross_revenue])` |
| Discount Amount | Item/order discounts granted | `sum(discount_amount)` | `SUM(fact_order_items[discount_amount])` |
| Refund Amount | Approved/completed return refunds | `sum(refund_amount)` on returns | `SUM(fact_returns[refund_amount])` |
| Net Revenue | Gross − discounts − refunds | `gross - discount - refund` | `SUM(fact_order_items[net_revenue])` |

## Orders & customers

| KPI | Definition |
|-----|------------|
| Total Orders | Count of distinct orders |
| Completed Orders | Orders with status `Delivered` |
| Cancelled Orders | Orders with status `Cancelled` |
| Returned Orders | Orders with status `Returned` OR at least one return record |
| Total Customers | Distinct customers who placed ≥1 order (unless stated otherwise) |
| Active Customers | Customers with an order in the last 90 days |
| Repeat Customers | Customers with `total_orders >= 2` |
| AOV | Gross revenue / total orders (or total_amount average — use consistently; Power BI measure uses Gross Revenue / Orders) |
| Average Items Per Order | `sum(quantity) / count(orders)` |
| Customer Lifetime Value | **Historical** net revenue per customer (not predictive LTV) |

## Quality & logistics

| KPI | Definition |
|-----|------------|
| Return Rate (orders) | Returned orders / total orders |
| Return Rate (items) | Returned items / sold items (product/seller views) |
| Cancellation Rate | Cancelled orders / total orders |
| Average Delivery Time | Mean `total_delivery_days` for delivered shipments |
| On-Time Delivery Rate | Deliveries with `delivery_date::date <= promised_delivery_date` / delivered with promise date |

## Customer segments (project rules)

| Segment | Rule |
|---------|------|
| New Customer | Exactly 1 order and last order ≤ 90 days |
| Returning Customer | ≥2 orders and last order ≤ 180 days |
| High Value | Top 20% by net revenue (quintile 1) |
| At Risk | ≥2 orders and last order between 91–180 days |
| Inactive | No order in >180 days (or zero orders) |

## RFM scoring

- Recency / Frequency / Monetary each scored 1–5 via `ntile(5)`
- Recency: lower days-since-last-order → higher score
- Segments: Champions, Loyal Customers, Potential Loyalists, At Risk, Needs Attention, Lost (see `config/settings.yaml`)

## Seller tiers

Documented thresholds in `config/settings.yaml` (revenue + max return/cancellation rates). Not industry-standard certifications.
