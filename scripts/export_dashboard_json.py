"""Export analytics dashboard data to JSON for Vercel static deployment."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.utils.config import PROJECT_ROOT
from src.utils.db import get_engine

OUTPUT = PROJECT_ROOT / "web" / "public" / "data" / "dashboard.json"


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


def export() -> Path:
    engine = get_engine()
    data: dict = {"generated_at": datetime.now(timezone.utc).isoformat(), "currency": "PKR"}

    queries = {
        "kpis": """
            SELECT COUNT(*) AS total_orders, COUNT(DISTINCT customer_key) AS total_customers,
                   SUM(gross_revenue) AS gross_revenue, SUM(net_revenue) AS net_revenue,
                   AVG(total_amount) AS aov, AVG(is_cancelled::numeric) AS cancellation_rate,
                   AVG(is_returned::numeric) AS return_rate
            FROM analytics.fact_orders
        """,
        "monthly": """
            SELECT d.year, d.month, TRIM(d.month_name) AS month_name,
                   SUM(f.net_revenue) AS net_revenue, SUM(f.gross_revenue) AS gross_revenue,
                   COUNT(*) AS orders, AVG(f.total_amount) AS aov
            FROM analytics.fact_orders f
            JOIN analytics.dim_date d ON f.date_key = d.date_key
            GROUP BY 1,2,3 ORDER BY 1,2
        """,
        "categories": """
            SELECT category_name, SUM(revenue) AS revenue, SUM(units_sold) AS units_sold,
                   AVG(return_rate) AS return_rate
            FROM analytics.dim_product GROUP BY 1 ORDER BY revenue DESC
        """,
        "provinces": """
            SELECT province, SUM(revenue) AS revenue, SUM(orders) AS orders
            FROM analytics.fct_location_performance GROUP BY 1 ORDER BY revenue DESC
        """,
        "cities": """
            SELECT city, province, revenue, orders, return_rate, avg_delivery_days
            FROM analytics.fct_location_performance
            WHERE revenue IS NOT NULL ORDER BY revenue DESC LIMIT 15
        """,
        "payments": """
            SELECT payment_method, COUNT(*) AS transactions,
                   AVG(is_successful::numeric) AS success_rate, SUM(payment_amount) AS amount
            FROM analytics.fact_payments GROUP BY 1 ORDER BY transactions DESC
        """,
        "segments": """
            SELECT customer_segment, COUNT(*) AS customers, SUM(total_spend) AS spend
            FROM analytics.dim_customer WHERE total_orders > 0
            GROUP BY 1 ORDER BY spend DESC
        """,
        "rfm": """
            SELECT rfm_segment, COUNT(*) AS customers
            FROM analytics.fct_customer_rfm GROUP BY 1 ORDER BY customers DESC
        """,
        "top_products": """
            SELECT product_name, category_name, revenue, units_sold, return_rate
            FROM analytics.dim_product ORDER BY revenue DESC LIMIT 15
        """,
        "sellers": """
            SELECT seller_name, seller_revenue, seller_return_rate, seller_cancellation_rate, seller_tier
            FROM analytics.dim_seller WHERE seller_revenue > 0
            ORDER BY seller_revenue DESC LIMIT 20
        """,
        "delivery_cities": """
            SELECT city, avg_delivery_days, on_time_delivery_rate, orders
            FROM analytics.fct_location_performance
            WHERE avg_delivery_days IS NOT NULL
            ORDER BY avg_delivery_days DESC LIMIT 15
        """,
        "returns": """
            SELECT return_reason, COUNT(*) AS returns, SUM(refund_amount) AS refund_amount
            FROM analytics.fact_returns GROUP BY 1 ORDER BY returns DESC
        """,
        "logistics": """
            SELECT AVG(total_delivery_days) AS avg_days,
                   AVG(on_time_flag::numeric) AS on_time_rate,
                   SUM(is_delayed) AS delayed_orders
            FROM analytics.fact_shipments WHERE total_delivery_days IS NOT NULL
        """,
    }

    with engine.connect() as conn:
        for key, sql in queries.items():
            df = pd.read_sql(text(sql), conn)
            if len(df) == 1 and key in ("kpis", "logistics"):
                data[key] = df.iloc[0].to_dict()
            else:
                data[key] = _df_to_records(df)

    monthly = pd.DataFrame(data["monthly"])
    monthly["growth_pct"] = monthly["net_revenue"].pct_change() * 100
    data["monthly"] = _df_to_records(monthly)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    engine.dispose()
    print(f"Exported dashboard JSON -> {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    export()
