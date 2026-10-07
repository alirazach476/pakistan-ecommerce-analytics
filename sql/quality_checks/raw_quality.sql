-- Sample SQL quality checks on raw layer
SELECT 'orders_null_customer' AS check_name, COUNT(*) AS failures
FROM raw.orders WHERE customer_id IS NULL
UNION ALL
SELECT 'orders_bad_status', COUNT(*)
FROM raw.orders
WHERE order_status NOT IN ('Pending','Confirmed','Shipped','Delivered','Cancelled','Returned')
UNION ALL
SELECT 'items_nonpositive_qty', COUNT(*)
FROM raw.order_items WHERE quantity <= 0
UNION ALL
SELECT 'orphan_order_customers', COUNT(*)
FROM raw.orders o
LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
