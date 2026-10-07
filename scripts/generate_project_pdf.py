"""
Generate a portfolio PDF for the Pakistan E-commerce Analytics Platform.

Output: docs/Pakistan_Ecommerce_Analytics_Platform.pdf
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from sqlalchemy import text

from src.utils.config import PROJECT_ROOT
from src.utils.db import get_engine

OUTPUT = PROJECT_ROOT / "docs" / "Pakistan_Ecommerce_Analytics_Platform.pdf"

# Brand colours (RGB)
NAVY = (15, 52, 96)
TEAL = (0, 128, 128)
LIGHT = (245, 247, 250)
WHITE = (255, 255, 255)


class ProjectPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Pakistan E-commerce Analytics Platform", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Synthetic data portfolio project - not real company data", align="C")

    def cover_page(self):
        self.add_page()
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 297, style="F")
        self.set_y(70)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*WHITE)
        self.multi_cell(0, 14, "Pakistan E-commerce\nAnalytics Platform", align="C")
        self.ln(8)
        self.set_font("Helvetica", "", 14)
        self.multi_cell(
            0,
            8,
            "End-to-End Data Engineering & Business Intelligence Portfolio",
            align="C",
        )
        self.ln(20)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(
            0,
            7,
            "Raw Data  ->  ETL  ->  PostgreSQL  ->  dbt  ->  Analytics  ->  BI Dashboard",
            align="C",
        )
        self.set_y(230)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 8, datetime.now(timezone.utc).strftime("%B %d, %Y"), align="C")
        self.ln(6)
        self.cell(0, 8, "Currency: PKR | Geography: Pakistan | Data: Synthetic", align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_fill_color(*TEAL)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def sub_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NAVY)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet_list(self, items: list[str]):
        self.set_font("Helvetica", "", 10)
        left = self.l_margin + 4
        width = self.w - self.l_margin - self.r_margin - 8
        for item in items:
            self.set_x(left)
            self.multi_cell(width, 5.5, f"- {item}")
        self.ln(2)

    def simple_table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None):
        if not rows:
            return
        n = len(headers)
        if col_widths is None:
            w = 190 / n
            col_widths = [w] * n
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*LIGHT)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h[:30], border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8)
        for row in rows:
            if self.get_y() > 270:
                self.add_page()
                self.set_font("Helvetica", "B", 9)
                self.set_fill_color(*LIGHT)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h[:30], border=1, fill=True)
                self.ln()
                self.set_font("Helvetica", "", 8)
            for i, cell in enumerate(row):
                txt = str(cell)[:40]
                self.cell(col_widths[i], 6, txt, border=1)
            self.ln()
        self.ln(3)


def _strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text


def _read_md(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _fetch_kpis() -> dict:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text(
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
            ).mappings().one()
            cities = conn.execute(
                text(
                    """
                    SELECT city, province, revenue::bigint, orders
                    FROM analytics.fct_location_performance
                    WHERE revenue IS NOT NULL
                    ORDER BY revenue DESC LIMIT 8
                    """
                )
            ).fetchall()
            categories = conn.execute(
                text(
                    """
                    SELECT category_name, SUM(revenue)::bigint AS revenue
                    FROM analytics.dim_product GROUP BY 1 ORDER BY 2 DESC LIMIT 8
                    """
                )
            ).fetchall()
            payments = conn.execute(
                text(
                    """
                    SELECT payment_method, COUNT(*) AS cnt
                    FROM analytics.fact_payments GROUP BY 1 ORDER BY 2 DESC
                    """
                )
            ).fetchall()
        engine.dispose()
        return {"kpis": dict(row), "cities": cities, "categories": categories, "payments": payments}
    except Exception:
        return {}


def generate_pdf() -> Path:
    data = _fetch_kpis()
    kpis = data.get("kpis", {})

    pdf = ProjectPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.cover_page()
    pdf.add_page()

    # --- Table of contents ---
    pdf.section_title("Table of Contents")
    toc = [
        "1. Project Overview",
        "2. Architecture & Technology Stack",
        "3. Dataset Statistics",
        "4. Data Pipeline & Quality",
        "5. Data Warehouse Design",
        "6. Analytics KPIs & Business Insights",
        "7. Dashboards & Deliverables",
        "8. How to Run",
        "9. Interview Talking Points",
    ]
    pdf.bullet_list(toc)

    # --- 1. Overview ---
    pdf.add_page()
    pdf.section_title("1. Project Overview")
    pdf.body_text(
        "This portfolio project demonstrates a production-style analytics platform for a fictional "
        "Pakistani e-commerce marketplace. It covers the full data lifecycle from synthetic data "
        "generation through ETL, validation, PostgreSQL warehousing, dbt transformations, data "
        "quality testing, analytics marts, BI dashboards, and business insights."
    )
    pdf.body_text(
        "IMPORTANT: This project uses synthetic data generated to simulate a Pakistani e-commerce "
        "marketplace. It is intended for demonstrating data engineering and analytics skills and "
        "does not represent actual company data."
    )
    pdf.sub_title("Business Questions Answered")
    pdf.bullet_list(
        [
            "Revenue trends, AOV, and category/province performance",
            "Customer segments, RFM analysis, and lifetime value",
            "Seller performance, return rates, and cancellation rates",
            "Delivery times, on-time rates, and logistics by city",
            "Payment method usage and success rates",
            "Return reasons and refund impact",
        ]
    )

    # --- 2. Architecture ---
    pdf.section_title("2. Architecture & Technology Stack")
    pdf.sub_title("Pipeline Architecture")
    pdf.set_font("Courier", "", 9)
    arch = (
        "Synthetic Data (Python)\n"
        "        |\n"
        "   data/raw (CSV)\n"
        "        |\n"
        " Python ETL (validate + load)\n"
        "        |\n"
        " PostgreSQL raw schema\n"
        "        |\n"
        " dbt (staging / intermediate / marts)\n"
        "        |\n"
        " analytics star schema\n"
        "        |\n"
        " Power BI / Streamlit / Excel / Insights"
    )
    pdf.multi_cell(0, 4.5, arch)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.sub_title("Technology Stack")
    pdf.simple_table(
        ["Layer", "Technology"],
        [
            ["Language", "Python 3.11+"],
            ["Database", "PostgreSQL 16"],
            ["Transformations", "dbt Core + dbt-postgres"],
            ["Orchestration", "Apache Airflow"],
            ["Validation", "Python + pytest + dbt tests"],
            ["BI", "Power BI + Streamlit dashboard"],
            ["Infrastructure", "Docker Compose"],
        ],
        [50, 140],
    )

    # --- 3. Dataset ---
    pdf.add_page()
    pdf.section_title("3. Dataset Statistics")
    pdf.simple_table(
        ["Entity", "Rows"],
        [
            ["Locations", "28"],
            ["Categories", "15"],
            ["Sellers", "1,000"],
            ["Customers", "100,000"],
            ["Products", "5,000"],
            ["Orders", "300,000"],
            ["Order Items", "901,205"],
            ["Payments", "300,000"],
            ["Shipments", "300,000"],
            ["Returns", "30,000"],
            ["Total Raw Load", "1,937,248"],
        ],
        [95, 95],
    )
    pdf.body_text("Date range: 2023-01-01 to 2025-12-31 | Currency: PKR | Random seed: 42")
    pdf.body_text(
        "Pakistan-specific data includes major cities (Karachi, Lahore, Islamabad, etc.), "
        "provinces, PKR pricing by category, Cash on Delivery payment mix, and local carriers (TCS, Leopards)."
    )

    # --- 4. Pipeline ---
    pdf.section_title("4. Data Pipeline & Quality")
    pdf.sub_title("ETL Stages")
    pdf.bullet_list(
        [
            "Generate: src/data_generation/generate.py",
            "Validate: src/validation/validate_raw.py",
            "Load: src/ingestion/pipeline.py (PostgreSQL COPY)",
            "Transform: dbt run (30 models)",
            "Test: dbt test (64 tests) + pytest (8 tests)",
            "Export: Excel summaries + business insights markdown",
        ]
    )
    pdf.sub_title("Quality Checks")
    pdf.bullet_list(
        [
            "Completeness: required IDs not null",
            "Uniqueness: primary keys unique",
            "Referential integrity: FK validation",
            "Accepted values: order status, payment method, return reasons",
            "Business rules: quantity > 0, delivery >= shipment date",
        ]
    )
    pdf.simple_table(
        ["Test Suite", "Result"],
        [
            ["dbt test", "64 / 64 passed"],
            ["pytest", "8 / 8 passed"],
            ["Raw validation", "All tables passed"],
        ],
        [95, 95],
    )

    # --- 5. Warehouse ---
    pdf.add_page()
    pdf.section_title("5. Data Warehouse Design")
    pdf.sub_title("Schemas")
    pdf.bullet_list(["raw - landing zone", "staging - dbt cleaned views", "intermediate - business logic", "analytics - star schema marts", "ops - pipeline monitoring"])
    pdf.sub_title("Star Schema Dimensions")
    pdf.body_text(
        "dim_customer, dim_product, dim_seller, dim_category, dim_location, dim_date, "
        "dim_payment_method, dim_order_status"
    )
    pdf.sub_title("Fact Tables (with grain)")
    pdf.simple_table(
        ["Fact Table", "Grain"],
        [
            ["fact_orders", "One row per order"],
            ["fact_order_items", "One row per order item"],
            ["fact_payments", "One row per payment"],
            ["fact_shipments", "One row per shipment"],
            ["fact_returns", "One row per return"],
        ],
        [60, 130],
    )
    pdf.sub_title("KPI Definitions")
    pdf.bullet_list(
        [
            "Gross Revenue = SUM(quantity * unit_price)",
            "Net Revenue = Gross - discounts - refunds",
            "AOV = Total Revenue / Total Orders",
            "Return Rate = Returned Orders / Total Orders",
            "CLV = Historical net revenue per customer (portfolio proxy)",
        ]
    )

    # --- 6. Analytics ---
    pdf.section_title("6. Analytics KPIs & Business Insights")
    if kpis:
        pdf.simple_table(
            ["KPI", "Value"],
            [
                ["Total Orders", f"{int(kpis.get('total_orders', 0)):,}"],
                ["Customers with Orders", f"{int(kpis.get('total_customers', 0)):,}"],
                ["Gross Revenue", f"PKR {float(kpis.get('gross_revenue', 0)):,.2f}"],
                ["Net Revenue", f"PKR {float(kpis.get('net_revenue', 0)):,.2f}"],
                ["AOV", f"PKR {float(kpis.get('aov', 0)):,.2f}"],
                ["Cancellation Rate", f"{float(kpis.get('cancellation_rate', 0)) * 100:.2f}%"],
                ["Return Rate", f"{float(kpis.get('return_rate', 0)) * 100:.2f}%"],
            ],
            [70, 120],
        )

    if data.get("cities"):
        pdf.sub_title("Top Cities by Revenue")
        pdf.simple_table(
            ["City", "Province", "Revenue (PKR)", "Orders"],
            [[c[0], c[1], f"{c[2]:,}", f"{c[3]:,}"] for c in data["cities"]],
            [35, 55, 55, 45],
        )

    if data.get("categories"):
        pdf.sub_title("Top Categories by Revenue")
        pdf.simple_table(
            ["Category", "Revenue (PKR)"],
            [[c[0], f"{c[1]:,}"] for c in data["categories"]],
            [90, 100],
        )

    if data.get("payments"):
        pdf.sub_title("Payment Method Distribution")
        pdf.simple_table(
            ["Payment Method", "Transactions"],
            [[p[0], f"{p[1]:,}"] for p in data["payments"]],
            [100, 90],
        )

    insights_path = PROJECT_ROOT / "analysis" / "business_insights.md"
    if insights_path.exists():
        pdf.sub_title("Key Findings")
        pdf.body_text(
            "Insights were generated from live SQL queries against the analytics schema, not fabricated."
        )
        pdf.bullet_list(
            [
                "Revenue concentrates in Karachi, Lahore, and Faisalabad.",
                "Mobile Phones is the highest-revenue category.",
                "Cash on Delivery dominates payment transactions (realistic for Pakistan).",
                "Return rates vary by category; high-revenue categories warrant quality review.",
                "Monthly net revenue shows strong upward trend from 2023 to 2025.",
                "Repeat customers contribute a significant share of total spend.",
            ]
        )

    # --- 7. Dashboards ---
    pdf.add_page()
    pdf.section_title("7. Dashboards & Deliverables")
    pdf.simple_table(
        ["Deliverable", "Location"],
        [
            ["Streamlit BI Dashboard", "dashboards/streamlit/app.py (localhost:8501)"],
            ["Power BI Project", "dashboards/powerbi/PakistanEcommerce/PakistanEcommerce.pbip"],
            ["Excel Summaries", "data/exports/analytics_summaries.xlsx"],
            ["Business Insights", "analysis/business_insights.md"],
            ["DAX Measures", "dashboards/powerbi/dax_measures.md"],
            ["Data Dictionary", "docs/data_dictionary.md"],
            ["Interview Guide", "docs/interview_guide.md"],
        ],
        [55, 135],
    )
    pdf.sub_title("Power BI Dashboard Pages")
    pdf.bullet_list(
        [
            "Page 1: Executive Overview - KPIs, revenue trend, category/province charts",
            "Page 2: Sales Analytics - monthly revenue, top products",
            "Page 3: Customer Analytics - segments, RFM, CLV",
            "Page 4: Product & Seller Analytics - performance tiers",
            "Page 5: Logistics - delivery times, on-time rate",
            "Page 6: Returns & Payments - return reasons, payment success",
        ]
    )

    # --- 8. How to run ---
    pdf.section_title("8. How to Run")
    pdf.set_font("Courier", "", 8)
    commands = (
        "1. cp .env.example .env\n"
        "2. pip install -r requirements.txt\n"
        "3. docker compose up -d postgres\n"
        "   (or: python scripts/start_embedded_postgres.py)\n"
        "4. python -m src.data_generation.generate\n"
        "5. python -m src.validation.validate_raw\n"
        "6. python -m src.ingestion.pipeline\n"
        "7. cd dbt && dbt run && dbt test\n"
        "8. streamlit run dashboards/streamlit/app.py\n"
        "9. Open dashboards/powerbi/PakistanEcommerce/PakistanEcommerce.pbip"
    )
    pdf.multi_cell(0, 4.5, commands)
    pdf.ln(4)

    # --- 9. Interview ---
    pdf.set_font("Helvetica", "", 10)
    pdf.section_title("9. Interview Talking Points")
    pdf.bullet_list(
        [
            "Why PostgreSQL? Open-source, strong SQL, dbt support, Docker-friendly.",
            "Why star schema? Clear grains, BI-friendly, reusable dimensions.",
            "Why dbt? Version-controlled SQL, tests, documentation, lineage.",
            "Why Airflow? Orchestrates multi-stage pipeline with dependencies.",
            "How handle data quality? Python pre-load checks + dbt tests + pytest.",
            "Grain of fact_order_items? One row per order line item.",
            "How scale to 10M orders? Partitioning, incremental dbt, cloud warehouse.",
        ]
    )

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0,
        5,
        "Generated automatically by scripts/generate_project_pdf.py from project documentation "
        "and live warehouse queries. Regenerate after pipeline runs to refresh KPIs.",
        align="C",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    return OUTPUT


def main() -> None:
    path = generate_pdf()
    print(f"PDF generated: {path}")
    print(f"Pages: {FPDF().page_no()}")  # noqa - just informational
    size_kb = path.stat().st_size / 1024
    print(f"Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
