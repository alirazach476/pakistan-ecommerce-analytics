# DAX Measures

Create these measures in a dedicated `Measures` table (or on `fact_orders`).

```dax
Total Revenue =
SUM ( fact_order_items[gross_revenue] )

Net Revenue =
SUM ( fact_order_items[net_revenue] )

Total Orders =
DISTINCTCOUNT ( fact_orders[order_id] )

Completed Orders =
CALCULATE (
    DISTINCTCOUNT ( fact_orders[order_id] ),
    fact_orders[order_status] = "Delivered"
)

Cancelled Orders =
CALCULATE (
    DISTINCTCOUNT ( fact_orders[order_id] ),
    fact_orders[order_status] = "Cancelled"
)

Returned Orders =
CALCULATE (
    DISTINCTCOUNT ( fact_orders[order_id] ),
    fact_orders[is_returned] = 1
)

Total Customers =
DISTINCTCOUNT ( fact_orders[customer_key] )

Active Customers =
CALCULATE (
    DISTINCTCOUNT ( fact_orders[customer_key] ),
    DATESINPERIOD ( dim_date[full_date], MAX ( dim_date[full_date] ), -90, DAY )
)

Repeat Customers =
COUNTROWS (
    FILTER ( dim_customer, dim_customer[total_orders] >= 2 )
)

AOV =
DIVIDE ( [Total Revenue], [Total Orders] )

Return Rate =
DIVIDE ( [Returned Orders], [Total Orders] )

Cancellation Rate =
DIVIDE ( [Cancelled Orders], [Total Orders] )

Average Delivery Days =
AVERAGE ( fact_shipments[total_delivery_days] )

On-Time Delivery Rate =
DIVIDE (
    SUM ( fact_shipments[on_time_flag] ),
    COUNTROWS ( FILTER ( fact_shipments, NOT ISBLANK ( fact_shipments[on_time_flag] ) ) )
)

Revenue Growth % =
VAR CurrentRevenue = [Net Revenue]
VAR PriorRevenue =
    CALCULATE ( [Net Revenue], DATEADD ( dim_date[full_date], -1, MONTH ) )
RETURN
    DIVIDE ( CurrentRevenue - PriorRevenue, PriorRevenue )

Order Growth % =
VAR CurrentOrders = [Total Orders]
VAR PriorOrders =
    CALCULATE ( [Total Orders], DATEADD ( dim_date[full_date], -1, MONTH ) )
RETURN
    DIVIDE ( CurrentOrders - PriorOrders, PriorOrders )
```

## Notes

- Use `fact_order_items` for product/category revenue to preserve item grain.
- Use `fact_orders` for order counts and order-level status KPIs.
- Format currency measures as PKR in Power BI (custom format or locale).
