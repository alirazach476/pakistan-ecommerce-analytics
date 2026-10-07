"""Export analytics summary tables to Excel for portfolio demonstrations."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.utils.config import get_settings
from src.utils.db import get_engine
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

QUERIES = {
    "Monthly Sales": """
        select
            d.year,
            d.month,
            d.month_name,
            count(*) as orders,
            sum(f.gross_revenue) as gross_revenue,
            sum(f.net_revenue) as net_revenue,
            avg(f.total_amount) as aov
        from analytics.fact_orders f
        join analytics.dim_date d on f.date_key = d.date_key
        group by 1, 2, 3
        order by 1, 2
    """,
    "Customer Summary": """
        select
            customer_segment,
            rfm_segment,
            count(*) as customers,
            avg(customer_lifetime_value) as avg_clv,
            sum(total_spend) as total_spend,
            avg(total_orders) as avg_orders
        from analytics.dim_customer
        where total_orders > 0
        group by 1, 2
        order by total_spend desc
    """,
    "Product Summary": """
        select
            category_name,
            count(*) as products,
            sum(units_sold) as units_sold,
            sum(revenue) as revenue,
            sum(net_revenue) as net_revenue,
            avg(return_rate) as avg_return_rate
        from analytics.dim_product
        group by 1
        order by revenue desc
    """,
    "Seller Summary": """
        select
            seller_tier,
            count(*) as sellers,
            sum(seller_revenue) as seller_revenue,
            avg(seller_return_rate) as avg_return_rate,
            avg(seller_cancellation_rate) as avg_cancellation_rate
        from analytics.dim_seller
        group by 1
        order by seller_revenue desc
    """,
    "Location Summary": """
        select city, province, region, orders, customers, revenue, net_revenue,
               aov, avg_delivery_days, on_time_delivery_rate, return_rate, cancellation_rate
        from analytics.fct_location_performance
        order by revenue desc nulls last
    """,
    "Returns Summary": """
        select
            return_reason,
            count(*) as returns,
            sum(refund_amount) as refund_amount
        from analytics.fact_returns
        group by 1
        order by returns desc
    """,
}


def export_summaries(output_path: Path | None = None) -> Path:
    settings = get_settings()
    output_path = output_path or (settings.exports_path / "analytics_summaries.xlsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    engine = get_engine()
    logger.info("Exporting analytics summaries to Excel")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet, sql in QUERIES.items():
            try:
                df = pd.read_sql(text(sql), engine)
                df.to_excel(writer, sheet_name=sheet[:31], index=False)
                logger.info("Wrote sheet %s (%s rows)", sheet, f"{len(df):,}")
            except Exception as exc:
                logger.warning("Skipping sheet %s: %s", sheet, exc)
                pd.DataFrame({"error": [str(exc)]}).to_excel(
                    writer, sheet_name=sheet[:31], index=False
                )
    engine.dispose()
    logger.info("Excel export completed: %s", output_path)
    return output_path


def main() -> None:
    path = export_summaries()
    print(f"Exported: {path}")


if __name__ == "__main__":
    main()
