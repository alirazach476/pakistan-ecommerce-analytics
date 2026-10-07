"""
Generate a Power BI Project (.pbip) connected to the local PostgreSQL analytics schema.

Open in Power BI Desktop (File > Open > PakistanEcommerce.pbip).
On first open, set PostgreSQL credentials for the analytics user.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from sqlalchemy import inspect, text

from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.db import get_engine

PROJECT_NAME = "PakistanEcommerce"
OUTPUT = PROJECT_ROOT / "dashboards" / "powerbi" / PROJECT_NAME

TABLES = [
    "dim_date",
    "dim_customer",
    "dim_product",
    "dim_seller",
    "dim_category",
    "dim_location",
    "dim_payment_method",
    "dim_order_status",
    "fact_orders",
    "fact_order_items",
    "fact_payments",
    "fact_shipments",
    "fact_returns",
    "fct_daily_revenue",
    "fct_location_performance",
    "fct_customer_rfm",
]

PG_TYPE_MAP = {
    "integer": "int64",
    "bigint": "int64",
    "smallint": "int64",
    "numeric": "decimal",
    "double precision": "double",
    "real": "double",
    "boolean": "boolean",
    "character varying": "string",
    "text": "string",
    "date": "dateTime",
    "timestamp without time zone": "dateTime",
    "timestamp with time zone": "dateTime",
}

RELATIONSHIPS = [
    ("fact_orders", "date_key", "dim_date", "date_key"),
    ("fact_order_items", "date_key", "dim_date", "date_key"),
    ("fact_payments", "date_key", "dim_date", "date_key"),
    ("fact_shipments", "date_key", "dim_date", "date_key"),
    ("fact_returns", "date_key", "dim_date", "date_key"),
    ("fact_orders", "customer_key", "dim_customer", "customer_key"),
    ("fact_order_items", "customer_key", "dim_customer", "customer_key"),
    ("fact_order_items", "product_key", "dim_product", "product_key"),
    ("fact_order_items", "seller_key", "dim_seller", "seller_key"),
    ("fact_orders", "location_key", "dim_location", "location_key"),
    ("fact_payments", "payment_method_key", "dim_payment_method", "payment_method_key"),
    ("fact_orders", "order_status_key", "dim_order_status", "order_status_key"),
    ("dim_product", "category_id", "dim_category", "category_id"),
]

MEASURES = [
    ("Total Revenue", "SUM(fact_order_items[gross_revenue])", "#,0"),
    ("Net Revenue", "SUM(fact_order_items[net_revenue])", "#,0"),
    ("Total Orders", "DISTINCTCOUNT(fact_orders[order_id])", "#,0"),
    ("Completed Orders", "CALCULATE(DISTINCTCOUNT(fact_orders[order_id]), fact_orders[order_status] = \"Delivered\")", "#,0"),
    ("Cancelled Orders", "CALCULATE(DISTINCTCOUNT(fact_orders[order_id]), fact_orders[order_status] = \"Cancelled\")", "#,0"),
    ("Returned Orders", "CALCULATE(DISTINCTCOUNT(fact_orders[order_id]), fact_orders[is_returned] = 1)", "#,0"),
    ("Total Customers", "DISTINCTCOUNT(fact_orders[customer_key])", "#,0"),
    ("AOV", "DIVIDE([Total Revenue], [Total Orders])", "#,0.00"),
    ("Return Rate", "DIVIDE([Returned Orders], [Total Orders])", "0.00%"),
    ("Cancellation Rate", "DIVIDE([Cancelled Orders], [Total Orders])", "0.00%"),
    ("Average Delivery Days", "AVERAGE(fact_shipments[total_delivery_days])", "#,0.0"),
    (
        "On-Time Delivery Rate",
        "DIVIDE(SUM(fact_shipments[on_time_flag]), COUNTROWS(FILTER(fact_shipments, NOT ISBLANK(fact_shipments[on_time_flag]))))",
        "0.00%",
    ),
]

REPORT_PAGES = [
    ("Executive Overview", "executive"),
    ("Sales Analytics", "sales"),
    ("Customer Analytics", "customers"),
    ("Product & Seller", "products"),
    ("Logistics", "logistics"),
    ("Returns & Payments", "returns"),
]


def _guid() -> str:
    return str(uuid.uuid4())


def _pg_type(col_type: str) -> str:
    base = col_type.split("(")[0].strip().lower()
    return PG_TYPE_MAP.get(base, "string")


def _m_query(table: str, settings) -> str:
    return f"""let
    Source = PostgreSQL.Database("{settings.postgres_host}", "{settings.postgres_db}", [Port={settings.postgres_port}]),
    Data = Source{{[Schema="analytics", Item="{table}"]}}[Data]
in
    Data"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_table_tmdl(table: str, columns: list[tuple[str, str]], settings) -> str:
    lines = [f"table {table}", f"    lineageTag: {_guid()}", ""]
    for col_name, col_type in columns:
        dtype = _pg_type(col_type)
        safe = col_name.replace("'", "''")
        lines.extend(
            [
                f"    column '{safe}'",
                f"        dataType: {dtype}",
                f"        lineageTag: {_guid()}",
                f"        sourceColumn: {col_name}",
                "",
            ]
        )
    m = _m_query(table, settings).replace("\n", "\n        ")
    lines.extend(
        [
            f"    partition {table} = m",
            "        mode: import",
            "        source =",
            f"            {m}",
            "",
        ]
    )
    return "\n".join(lines)


def _build_relationships_tmdl() -> str:
    lines: list[str] = []
    for from_table, from_col, to_table, to_col in RELATIONSHIPS:
        lines.extend(
            [
                f"relationship {_guid()}",
                f"    fromColumn: {from_table}.{from_col}",
                f"    toColumn: {to_table}.{to_col}",
                "",
            ]
        )
    return "\n".join(lines)


def _build_measures_tmdl() -> str:
    lines = ["table KPIs", f"    lineageTag: {_guid()}", ""]
    for name, expr, fmt in MEASURES:
        lines.extend(
            [
                f"    measure '{name}' = {expr}",
                f"        formatString: {fmt}",
                "",
            ]
        )
    return "\n".join(lines)


def _projection(field: str, table: str) -> dict:
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": field,
            }
        },
        "queryRef": f"{table}.{field}",
        "nativeQueryRef": field,
    }


def _card_visual(name: str, measure: str, x: int, y: int, w: int = 180, h: int = 100) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": 0, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [_projection(measure, "KPIs")],
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{measure}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                        }
                    }
                ]
            },
        },
    }


def _write_page(page_id: str, page_name: str, slug: str) -> None:
    report_def = OUTPUT / f"{PROJECT_NAME}.Report" / "definition"
    page_dir = report_def / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)

    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
        "name": page_id,
        "displayName": page_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
        "objects": {},
    }
    _write(page_dir / "page.json", json.dumps(page_json, indent=2))

    visuals_dir = page_dir / "visuals"
    if slug == "executive":
        cards = [
            ("v_net_rev", "Net Revenue", 20, 20),
            ("v_orders", "Total Orders", 220, 20),
            ("v_customers", "Total Customers", 420, 20),
            ("v_aov", "AOV", 620, 20),
            ("v_return", "Return Rate", 820, 20),
            ("v_cancel", "Cancellation Rate", 1020, 20),
        ]
        for vid, measure, x, y in cards:
            vdir = visuals_dir / vid
            vdir.mkdir(parents=True, exist_ok=True)
            _write(vdir / "visual.json", json.dumps(_card_visual(vid, measure, x, y), indent=2))


def generate() -> Path:
    settings = get_settings()
    engine = get_engine()
    inspector = inspect(engine)

    if OUTPUT.exists():
        import shutil

        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    sm_dir = OUTPUT / f"{PROJECT_NAME}.SemanticModel" / "definition"
    tables_dir = sm_dir / "tables"
    tables_dir.mkdir(parents=True)

    for table in TABLES:
        cols = [
            (c["name"], str(c["type"]))
            for c in inspector.get_columns(table, schema="analytics")
        ]
        _write(tables_dir / f"{table}.tmdl", _build_table_tmdl(table, cols, settings))

    _write(tables_dir / "KPIs.tmdl", _build_measures_tmdl())
    _write(sm_dir / "database.tmdl", "database\n\tcompatibilityLevel: 1567\n")
    _write(
        sm_dir / "model.tmdl",
        "\n".join(
            [
                "model Model",
                "\tculture: en-US",
                "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
                "\tsourceQueryCulture: en-US",
                f"\tdataAccessOptions legacyRedirects",
                "\tannotation PBI_QueryOrder = []",
                "",
                "ref table KPIs",
                *[f"ref table {t}" for t in TABLES],
                "",
            ]
        ),
    )
    _write(sm_dir / "relationships.tmdl", _build_relationships_tmdl())

    _write(
        OUTPUT / f"{PROJECT_NAME}.SemanticModel" / "definition.pbism",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
                "version": "4.2",
                "settings": {},
            },
            indent=2,
        ),
    )
    _write(
        OUTPUT / f"{PROJECT_NAME}.SemanticModel" / ".platform",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                "metadata": {"type": "SemanticModel", "displayName": "Pakistan E-commerce Analytics"},
                "config": {"version": "2.0", "logicalId": _guid()},
            },
            indent=2,
        ),
    )

    report_dir = OUTPUT / f"{PROJECT_NAME}.Report"
    _write(
        report_dir / "definition.pbir",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
                "version": "4.0",
                "datasetReference": {"byPath": {"path": f"../{PROJECT_NAME}.SemanticModel"}},
            },
            indent=2,
        ),
    )
    _write(
        report_dir / ".platform",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                "metadata": {"type": "Report", "displayName": "Pakistan E-commerce Dashboard"},
                "config": {"version": "2.0", "logicalId": _guid()},
            },
            indent=2,
        ),
    )

    report_def = report_dir / "definition"
    page_ids = {slug: _guid() for _, slug in REPORT_PAGES}
    pages_manifest = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [page_ids[s] for _, s in REPORT_PAGES],
        "activePageName": page_ids["executive"],
    }
    _write(report_def / "pages" / "pages.json", json.dumps(pages_manifest, indent=2))
    _write(
        report_def / "report.json",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.2.0/schema.json",
                "themeCollection": {"baseTheme": {"name": "CY24SU10", "type": "SharedResources"}},
                "layoutOptimization": "None",
                "resourcePackages": [
                    {
                        "name": "SharedResources",
                        "type": "SharedResources",
                        "items": [
                            {
                                "name": "CY24SU10",
                                "path": "BaseThemes/CY24SU10.json",
                                "type": "BaseTheme",
                            }
                        ],
                    }
                ],
            },
            indent=2,
        ),
    )
    _write(report_def / "version.json", json.dumps({"version": "2.0.0"}, indent=2))

    for page_name, slug in REPORT_PAGES:
        _write_page(page_ids[slug], page_name, slug)

    pbip_path = OUTPUT / f"{PROJECT_NAME}.pbip"
    _write(
        pbip_path,
        json.dumps(
            {
                "version": "1.0",
                "artifacts": [{"report": {"path": f"{PROJECT_NAME}.Report"}}],
                "settings": {"enableAutoRecovery": True},
            },
            indent=2,
        ),
    )

    _write(
        OUTPUT / ".gitignore",
        "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n",
    )

    readme = f"""# Pakistan E-commerce Power BI Project

## Open in Power BI Desktop

1. Install [Power BI Desktop](https://apps.microsoft.com/detail/9ntxr16hnw1t) from Microsoft Store.
2. Open `{PROJECT_NAME}.pbip` in this folder.
3. When prompted, set PostgreSQL credentials:
   - Server: `{settings.postgres_host}:{settings.postgres_port}`
   - Database: `{settings.postgres_db}`
   - User: `{settings.postgres_user}`
4. Click **Transform Data** > **Refresh** if tables are empty on first load.

## Included

- Semantic model (`{PROJECT_NAME}.SemanticModel`) — analytics schema tables + KPI measures
- Report (`{PROJECT_NAME}.Report`) — 6 pages; Executive Overview has KPI cards
- Star-schema relationships pre-defined

## Regenerate

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/generate_powerbi_project.py
```

Ensure PostgreSQL is running and dbt models exist in `analytics` schema.
"""
    _write(OUTPUT / "README.md", readme)

    engine.dispose()
    print(f"Generated Power BI project: {pbip_path}")
    return pbip_path


if __name__ == "__main__":
    generate()
