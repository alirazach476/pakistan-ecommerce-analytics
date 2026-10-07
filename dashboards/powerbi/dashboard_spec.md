# Power BI Dashboard Specification

> **Generated project:** `dashboards/powerbi/PakistanEcommerce/PakistanEcommerce.pbip`  
> Open in Power BI Desktop · PostgreSQL credentials from `.env`  
> **Live web dashboard (no PBI install):** run `scripts/start_dashboard.ps1` → http://localhost:8501

Build a 6-page report. Use a clean enterprise style (avoid decorative clutter). Currency = PKR.

## Page 1 — Executive Overview

**KPIs (cards):** Revenue · Net Revenue · Orders · Customers · AOV · Return Rate · Cancellation Rate

**Charts:**
- Revenue over time (line, month)
- Orders over time (line, month)
- Revenue by category (bar)
- Revenue by province (bar or map)
- Top 10 products (bar)
- Payment method distribution (donut)

## Page 2 — Sales Analytics

- Monthly revenue & orders
- Revenue by category / product / province
- AOV trend
- Sales growth % (month-over-month)

## Page 3 — Customer Analytics

- New vs returning (from `customer_segment`)
- Segment distribution
- RFM segments
- CLV distribution
- Repeat purchase rate

## Page 4 — Product & Seller Analytics

- Top / bottom products by revenue
- Seller revenue and order volume
- Return rate by seller
- Cancellation rate by seller
- Seller tier breakdown

## Page 5 — Logistics

- Average delivery time
- On-time delivery rate
- Delivery time by city
- Delayed orders
- Cancellation rate

## Page 6 — Returns & Payments

- Return rate trend
- Return reasons
- Refund amount
- Payment method usage
- Payment success / failure
- Refund trends

## Screenshot placeholders

Add exported PNG screenshots to `dashboards/screenshots/` after building the PBIX locally:

- `01_executive_overview.png`
- `02_sales_analytics.png`
- `03_customer_analytics.png`
- `04_product_seller.png`
- `05_logistics.png`
- `06_returns_payments.png`
