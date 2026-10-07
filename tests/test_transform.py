"""Tests for ingestion transforms and business rules."""

from __future__ import annotations

import pandas as pd

from src.ingestion.transform import transform_table


def test_transform_adds_audit_columns():
    df = pd.DataFrame(
        {
            "order_id": [1],
            "customer_id": [1],
            "order_date": ["2024-01-01 10:00:00"],
            "order_status": ["Delivered"],
            "total_amount": [100],
            "shipping_fee": [0],
            "discount_amount": [0],
        }
    )
    out = transform_table("orders", df, "orders.csv")
    assert "loaded_at" in out.columns
    assert "source_file" in out.columns
    assert out.loc[0, "source_file"] == "orders.csv"


def test_transform_filters_non_positive_quantity():
    df = pd.DataFrame(
        {
            "order_item_id": [1, 2],
            "order_id": [1, 1],
            "product_id": [1, 2],
            "quantity": [2, 0],
            "unit_price": [10, 10],
            "discount_amount": [0, 0],
            "line_total": [20, 0],
        }
    )
    out = transform_table("order_items", df, "order_items.csv")
    assert len(out) == 1
    assert out.iloc[0]["order_item_id"] == 1
