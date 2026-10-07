"""
Pakistan E-commerce Analytics — interactive BI dashboard (PostgreSQL analytics schema).

Run:
  streamlit run dashboards/streamlit/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.db import get_engine  # noqa: E402

st.set_page_config(
    page_title="Pakistan E-commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = px.colors.qualitative.Set2


@st.cache_resource
def get_db():
    return get_engine()


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    engine = get_db()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def fmt_pkr(value: float) -> str:
    if pd.isna(value):
        return "PKR 0"
    if abs(value) >= 1_000_000_000:
        return f"PKR {value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"PKR {value / 1_000_000:.2f}M"
    return f"PKR {value:,.0f}"


def kpi_row(df: pd.DataFrame) -> None:
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    row = df.iloc[0]
    c1.metric("Gross Revenue", fmt_pkr(row["gross_revenue"]))
    c2.metric("Net Revenue", fmt_pkr(row["net_revenue"]))
    c3.metric("Orders", f"{int(row['total_orders']):,}")
    c4.metric("Customers", f"{int(row['total_customers']):,}")
    c5.metric("AOV", fmt_pkr(row["aov"]))
    c6.metric("Return Rate", f"{row['return_rate'] * 100:.1f}%")
    c7.metric("Cancellation Rate", f"{row['cancellation_rate'] * 100:.1f}%")


def page_executive() -> None:
    st.title("Executive Overview")
    st.caption("Synthetic Pakistani e-commerce marketplace · analytics schema · PKR")

    kpis = query(
        """
        SELECT
            COUNT(*) AS total_orders,
            COUNT(DISTINCT customer_key) AS total_customers,
            SUM(gross_revenue) AS gross_revenue,
            SUM(net_revenue) AS net_revenue,
            AVG(total_amount) AS aov,
            AVG(is_cancelled::numeric) AS cancellation_rate,
            AVG(is_returned::numeric) AS return_rate
        FROM analytics.fact_orders
        """
    )
    kpi_row(kpis)

    monthly = query(
        """
        SELECT d.year, d.month, d.month_name,
               SUM(f.net_revenue) AS net_revenue,
               COUNT(*) AS orders
        FROM analytics.fact_orders f
        JOIN analytics.dim_date d ON f.date_key = d.date_key
        GROUP BY 1,2,3 ORDER BY 1,2
        """
    )
    monthly["period"] = monthly["month_name"].str.strip() + " " + monthly["year"].astype(str)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(monthly, x="period", y="net_revenue", title="Net Revenue Over Time", markers=True)
        fig.update_layout(xaxis_title="", yaxis_title="Net Revenue (PKR)", height=380)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(monthly, x="period", y="orders", title="Orders Over Time", markers=True, color_discrete_sequence=[PALETTE[1]])
        fig.update_layout(xaxis_title="", yaxis_title="Orders", height=380)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    category = query(
        """
        SELECT category_name, SUM(revenue) AS revenue
        FROM analytics.dim_product GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """
    )
    with c3:
        fig = px.bar(category, x="category_name", y="revenue", title="Revenue by Category (Top 10)", color="category_name")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue (PKR)", height=380)
        st.plotly_chart(fig, use_container_width=True)

    province = query(
        """
        SELECT province, SUM(revenue) AS revenue
        FROM analytics.fct_location_performance GROUP BY 1 ORDER BY 2 DESC
        """
    )
    with c4:
        fig = px.bar(province, x="province", y="revenue", title="Revenue by Province", color="province")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue (PKR)", height=380)
        st.plotly_chart(fig, use_container_width=True)

    payments = query(
        """
        SELECT payment_method, COUNT(*) AS transactions
        FROM analytics.fact_payments GROUP BY 1 ORDER BY 2 DESC
        """
    )
    fig = px.pie(payments, names="payment_method", values="transactions", title="Payment Method Distribution", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)


def page_sales() -> None:
    st.title("Sales Analytics")
    monthly = query(
        """
        SELECT d.year, d.month, d.month_name,
               SUM(f.gross_revenue) AS gross_revenue,
               SUM(f.net_revenue) AS net_revenue,
               COUNT(*) AS orders,
               AVG(f.total_amount) AS aov
        FROM analytics.fact_orders f
        JOIN analytics.dim_date d ON f.date_key = d.date_key
        GROUP BY 1,2,3 ORDER BY 1,2
        """
    )
    monthly["period"] = monthly["month_name"].str.strip() + " " + monthly["year"].astype(str)
    monthly["growth_pct"] = monthly["net_revenue"].pct_change() * 100

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(monthly, x="period", y="net_revenue", title="Monthly Net Revenue"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(monthly, x="period", y="orders", title="Monthly Orders", color_discrete_sequence=[PALETTE[2]]), use_container_width=True)

    top_products = query(
        """
        SELECT product_name, category_name, revenue, units_sold
        FROM analytics.dim_product ORDER BY revenue DESC LIMIT 15
        """
    )
    st.plotly_chart(
        px.bar(top_products, x="product_name", y="revenue", color="category_name", title="Top 15 Products by Revenue"),
        use_container_width=True,
    )

    st.line_chart(monthly.set_index("period")[["growth_pct"]], height=260)


def page_customers() -> None:
    st.title("Customer Analytics")
    segments = query(
        """
        SELECT customer_segment, COUNT(*) AS customers, SUM(total_spend) AS spend
        FROM analytics.dim_customer WHERE total_orders > 0
        GROUP BY 1 ORDER BY spend DESC
        """
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(segments, x="customer_segment", y="customers", title="Customers by Segment"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(segments, x="customer_segment", y="spend", title="Spend by Segment", color_discrete_sequence=[PALETTE[3]]), use_container_width=True)

    rfm = query(
        """
        SELECT rfm_segment, COUNT(*) AS customers
        FROM analytics.fct_customer_rfm GROUP BY 1 ORDER BY 2 DESC
        """
    )
    st.plotly_chart(px.treemap(rfm, path=["rfm_segment"], values="customers", title="RFM Segments"), use_container_width=True)

    clv = query(
        """
        SELECT customer_lifetime_value FROM analytics.dim_customer
        WHERE total_orders > 0 ORDER BY customer_lifetime_value DESC LIMIT 5000
        """
    )
    st.plotly_chart(px.histogram(clv, x="customer_lifetime_value", nbins=40, title="Customer Lifetime Value Distribution"), use_container_width=True)


def page_products() -> None:
    st.title("Product & Seller Analytics")
    c1, c2 = st.columns(2)
    top = query("SELECT product_name, revenue FROM analytics.dim_product ORDER BY revenue DESC LIMIT 10")
    bottom = query("SELECT product_name, revenue FROM analytics.dim_product WHERE units_sold > 0 ORDER BY revenue ASC LIMIT 10")
    with c1:
        st.plotly_chart(px.bar(top, x="product_name", y="revenue", title="Top Products"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(bottom, x="product_name", y="revenue", title="Lowest Revenue Products (with sales)", color_discrete_sequence=[PALETTE[5]]), use_container_width=True)

    sellers = query(
        """
        SELECT seller_name, seller_revenue, seller_return_rate, seller_cancellation_rate, seller_tier
        FROM analytics.dim_seller WHERE seller_revenue > 0
        ORDER BY seller_revenue DESC LIMIT 20
        """
    )
    st.plotly_chart(
        px.scatter(
            sellers,
            x="seller_revenue",
            y="seller_return_rate",
            size="seller_revenue",
            color="seller_tier",
            hover_name="seller_name",
            title="Seller Revenue vs Return Rate",
        ),
        use_container_width=True,
    )


def page_logistics() -> None:
    st.title("Logistics")
    delivery = query(
        """
        SELECT AVG(total_delivery_days) AS avg_days,
               AVG(on_time_flag::numeric) AS on_time_rate,
               SUM(is_delayed) AS delayed_orders
        FROM analytics.fact_shipments
        WHERE total_delivery_days IS NOT NULL
        """
    )
    d = delivery.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Delivery Days", f"{d['avg_days']:.1f}")
    c2.metric("On-Time Rate", f"{d['on_time_rate'] * 100:.1f}%")
    c3.metric("Delayed Orders", f"{int(d['delayed_orders']):,}")

    by_city = query(
        """
        SELECT city, avg_delivery_days, on_time_delivery_rate, orders
        FROM analytics.fct_location_performance
        WHERE avg_delivery_days IS NOT NULL
        ORDER BY avg_delivery_days DESC LIMIT 15
        """
    )
    st.plotly_chart(px.bar(by_city, x="city", y="avg_delivery_days", title="Average Delivery Days by City (slowest 15)"), use_container_width=True)


def page_returns() -> None:
    st.title("Returns & Payments")
    c1, c2 = st.columns(2)
    reasons = query(
        """
        SELECT return_reason, COUNT(*) AS returns, SUM(refund_amount) AS refund_amount
        FROM analytics.fact_returns GROUP BY 1 ORDER BY 2 DESC
        """
    )
    with c1:
        st.plotly_chart(px.bar(reasons, x="return_reason", y="returns", title="Returns by Reason"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(reasons, x="return_reason", y="refund_amount", title="Refund Amount by Reason", color_discrete_sequence=[PALETTE[7]]), use_container_width=True)

    pay = query(
        """
        SELECT payment_method,
               COUNT(*) AS transactions,
               AVG(is_successful::numeric) AS success_rate,
               SUM(payment_amount) AS amount
        FROM analytics.fact_payments GROUP BY 1 ORDER BY transactions DESC
        """
    )
    st.plotly_chart(px.bar(pay, x="payment_method", y="success_rate", title="Payment Success Rate by Method", color="payment_method"), use_container_width=True)


PAGES = {
    "Executive Overview": page_executive,
    "Sales Analytics": page_sales,
    "Customer Analytics": page_customers,
    "Product & Seller": page_products,
    "Logistics": page_logistics,
    "Returns & Payments": page_returns,
}

with st.sidebar:
    st.header("Pakistan E-commerce")
    st.markdown("**Live BI Dashboard** connected to PostgreSQL `analytics` schema.")
    st.info("Synthetic portfolio data · PKR")
    choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.markdown("**Power BI Desktop**")
    st.code("dashboards/powerbi/PakistanEcommerce/PakistanEcommerce.pbip", language="text")
    st.caption("Open the .pbip file in Power BI Desktop after installing from Microsoft Store.")

PAGES[choice]()
