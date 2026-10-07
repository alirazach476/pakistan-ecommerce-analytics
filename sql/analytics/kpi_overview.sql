-- Executive KPI overview (run after dbt)
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT customer_key) AS total_customers,
    SUM(gross_revenue) AS gross_revenue,
    SUM(net_revenue) AS net_revenue,
    AVG(total_amount) AS aov,
    AVG(is_cancelled::numeric) AS cancellation_rate,
    AVG(is_returned::numeric) AS return_rate
FROM analytics.fact_orders;
