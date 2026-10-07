"""Generate business insights markdown from actual warehouse query results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.db import get_engine
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def _q(engine, sql: str) -> pd.DataFrame:
    return pd.read_sql(text(sql), engine)


def generate_insights(output_path: Path | None = None) -> Path:
    settings = get_settings()
    output_path = output_path or (PROJECT_ROOT / "analysis" / "business_insights.md")
    engine = get_engine()
    logger.info("Generating business insights from analytics schema")

    kpis = _q(
        engine,
        """
        select
            count(*) as total_orders,
            count(distinct customer_key) as total_customers,
            sum(gross_revenue) as gross_revenue,
            sum(net_revenue) as net_revenue,
            avg(total_amount) as aov,
            avg(is_cancelled::numeric) as cancellation_rate,
            avg(is_returned::numeric) as return_rate
        from analytics.fact_orders
        """,
    ).iloc[0]

    top_cities = _q(
        engine,
        """
        select city, province, revenue, orders, return_rate, avg_delivery_days
        from analytics.fct_location_performance
        where revenue is not null
        order by revenue desc
        limit 10
        """,
    )

    category_returns = _q(
        engine,
        """
        select
            category_name,
            sum(revenue) as revenue,
            avg(return_rate) as return_rate,
            sum(units_sold) as units_sold
        from analytics.dim_product
        group by 1
        order by revenue desc
        """,
    )

    seller_issues = _q(
        engine,
        """
        select seller_name, seller_revenue, seller_return_rate, seller_cancellation_rate, seller_tier
        from analytics.dim_seller
        where seller_revenue > 0
        order by seller_revenue desc
        limit 15
        """,
    )

    monthly = _q(
        engine,
        """
        select d.year, d.month, sum(f.net_revenue) as net_revenue, count(*) as orders
        from analytics.fact_orders f
        join analytics.dim_date d on f.date_key = d.date_key
        group by 1, 2
        order by 1, 2
        """,
    )

    repeat = _q(
        engine,
        """
        select
            sum(case when total_orders >= 2 then 1 else 0 end)::numeric
                / nullif(count(*), 0) as repeat_customer_rate,
            sum(case when total_orders >= 2 then total_spend else 0 end) as repeat_spend,
            sum(total_spend) as all_spend
        from analytics.dim_customer
        where total_orders > 0
        """,
    ).iloc[0]

    payments = _q(
        engine,
        """
        select
            payment_method,
            count(*) as transactions,
            avg(is_successful::numeric) as success_rate,
            sum(payment_amount) as amount
        from analytics.fact_payments
        group by 1
        order by transactions desc
        """,
    )

    delivery_cities = _q(
        engine,
        """
        select city, avg_delivery_days, on_time_delivery_rate, orders
        from analytics.fct_location_performance
        where avg_delivery_days is not null
        order by avg_delivery_days desc
        limit 10
        """,
    )

    segments = _q(
        engine,
        """
        select customer_segment, count(*) as customers, sum(total_spend) as spend
        from analytics.dim_customer
        where total_orders > 0
        group by 1
        order by spend desc
        """,
    )

    high_return_products = _q(
        engine,
        """
        select product_name, category_name, revenue, return_rate, units_sold
        from analytics.dim_product
        where units_sold >= 50
        order by return_rate desc, revenue desc
        limit 15
        """,
    )

    # Monthly growth
    monthly = monthly.copy()
    monthly["net_revenue_growth_pct"] = monthly["net_revenue"].pct_change() * 100

    def fmt_money(x) -> str:
        try:
            return f"PKR {float(x):,.2f}"
        except Exception:
            return str(x)

    def df_md(df: pd.DataFrame) -> str:
        if df.empty:
            return "_No rows_"
        return df.to_markdown(index=False)

    lines = [
        "# Business Insights — Pakistan E-commerce Analytics Platform",
        "",
        "> Generated from the **analytics** schema in PostgreSQL. "
        "Figures reflect **synthetic** marketplace data, not a real company.",
        "",
        f"_Generated at: {datetime.now(timezone.utc).isoformat()}_",
        "",
        "## Executive snapshot",
        "",
        f"- **Total orders:** {int(kpis['total_orders']):,}",
        f"- **Customers with orders:** {int(kpis['total_customers']):,}",
        f"- **Gross revenue:** {fmt_money(kpis['gross_revenue'])}",
        f"- **Net revenue:** {fmt_money(kpis['net_revenue'])}",
        f"- **Average order value (AOV):** {fmt_money(kpis['aov'])}",
        f"- **Cancellation rate:** {float(kpis['cancellation_rate']) * 100:.2f}%",
        f"- **Return-related order rate:** {float(kpis['return_rate']) * 100:.2f}%",
        "",
        "## 1. Which cities contribute most to revenue?",
        "",
        df_md(top_cities),
        "",
        "## 2. Which categories have high revenue and elevated return rates?",
        "",
        df_md(category_returns),
        "",
        "## 3. Which sellers have high sales (fulfillment risk signals)?",
        "",
        "Top sellers by revenue with return/cancellation rates (synthetic):",
        "",
        df_md(seller_issues),
        "",
        "## 4. What is the monthly growth trend?",
        "",
        df_md(monthly),
        "",
        "## 5. What percentage of customers are repeat customers?",
        "",
        f"- **Repeat customer rate:** {float(repeat['repeat_customer_rate']) * 100:.2f}%",
        f"- **Spend from repeat customers:** {fmt_money(repeat['repeat_spend'])} "
        f"of {fmt_money(repeat['all_spend'])}",
        "",
        "## 6. Which payment methods dominate?",
        "",
        df_md(payments),
        "",
        "## 7. Which cities have delivery problems?",
        "",
        "Highest average delivery days:",
        "",
        df_md(delivery_cities),
        "",
        "## 8. Which customer segments contribute most revenue?",
        "",
        df_md(segments),
        "",
        "## 9. Which products have high sales and high return rates?",
        "",
        df_md(high_return_products),
        "",
        "## 10. Operational patterns observed",
        "",
        "- Payment mix is dominated by methods with the highest transaction counts in the table above "
        "(expected Cash on Delivery weight in a Pakistani marketplace simulation).",
        "- Revenue concentrates in a small set of large cities — see city ranking.",
        "- Category return rates vary; categories with both high revenue and higher return rates "
        "are priority quality-review candidates.",
        "- Seller tiers (`Platinum`/`Gold`/`Silver`/`Bronze`) encode documented revenue and quality thresholds "
        "in `config/settings.yaml` — not universal industry standards.",
        "",
        "## Methodology notes",
        "",
        "- **Gross revenue** = sum of `quantity * unit_price` at order-item grain.",
        "- **Net revenue** = gross − item discounts − refunds (order-level aggregation in `int_order_metrics`).",
        "- **CLV** in this project is historical net revenue per customer (not a predictive LTV model).",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    sql_path = PROJECT_ROOT / "analysis" / "sql_analysis.md"
    sql_path.write_text(
        "# SQL Analysis Queries\n\n"
        "The insights above were produced by `src/transformation/generate_insights.py` "
        "against the `analytics` schema. Re-run after dbt:\n\n"
        "```bash\npython -m src.transformation.generate_insights\n```\n",
        encoding="utf-8",
    )

    engine.dispose()
    logger.info("Wrote insights to %s", output_path)
    return output_path


def main() -> None:
    path = generate_insights()
    print(f"Insights written to {path}")


if __name__ == "__main__":
    main()
